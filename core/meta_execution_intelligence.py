from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import uuid4
from statistics import mean

from .execution_evidence_chain import ExecutionEvidenceChain


@dataclass(frozen=True)
class ExecutionObservation:
    route: str
    task_class: str
    status: str
    duration_ms: float
    error_class: str | None
    observed_at: str
    event_nonce: str
    event_id: str


class MetaExecutionIntelligence:
    """Bounded, append-only route learning from verified execution outcomes."""

    def __init__(self, path: str | Path, failure_threshold: int = 3):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.failure_threshold = max(1, int(failure_threshold))

    @staticmethod
    def _fingerprint(payload: dict) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
    def observe(
        self,
        route: str,
        task_class: str,
        status: str,
        duration_ms: float,
        error_class: str | None = None,
    ) -> ExecutionObservation:
        observed_at = datetime.now(timezone.utc).isoformat()
        payload = {
            "route": str(route),
            "task_class": str(task_class),
            "status": str(status),
            "duration_ms": float(duration_ms),
            "error_class": error_class,
            "observed_at": observed_at,
            "event_nonce": uuid4().hex,
        }
        integrity = self.verify()
        if not integrity["verified"]:
            raise ValueError(integrity["reason"])
        event = dict(payload)
        event["event_id"] = self._fingerprint(payload)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        return ExecutionObservation(**event)

    def replay(self, task_class: str | None = None) -> list[dict]:
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if task_class is None or record["task_class"] == task_class:
                records.append(record)
        return records

    def verify(self) -> dict:
        if not self.path.exists():
            return {"verified": True, "reason": "EMPTY_CHAIN", "event_count": 0, "chain_head": ExecutionEvidenceChain.GENESIS}
        seen = set()
        previous_observed_at = None
        records = self.replay()
        for record in records:
            event_id = record.get("event_id")
            if not event_id or event_id in seen:
                return {"verified": False, "reason": "DUPLICATE_EVENT_ID", "event_count": len(records), "chain_head": None}
            seen.add(event_id)
            body = {k: record.get(k) for k in ("route", "task_class", "status", "duration_ms", "error_class", "observed_at", "event_nonce")}
            if event_id != self._fingerprint(body):
                return {"verified": False, "reason": "EVENT_FINGERPRINT_MISMATCH", "event_count": len(records), "chain_head": None}
            observed_at = record.get("observed_at")
            if previous_observed_at is not None and observed_at < previous_observed_at:
                return {"verified": False, "reason": "OBSERVATION_TIME_ROLLBACK", "event_count": len(records), "chain_head": None}
            previous_observed_at = observed_at
        chain = ExecutionEvidenceChain.compute(records)
        return {"verified": True, "reason": "CHAIN_VALID", "event_count": len(records), "chain_head": chain["chain_head"]}

    def verified_chain_state(self) -> dict:
        result = self.verify()
        return {
            "event_count": result["event_count"],
            "chain_head": result["chain_head"],
            "verified": result["verified"],
        }

    def _route_stats(self, task_class: str, route: str) -> tuple[float, float, int, int]:
        records = [r for r in self.replay(task_class) if r["route"] == route]
        successes = sum(r["status"] == "success" for r in records)
        failures = len(records) - successes
        consecutive_failures = 0
        for record in reversed(records):
            if record["status"] == "success":
                break
            consecutive_failures += 1
        success_rate = successes / len(records) if records else 0.0
        latency = mean(float(r["duration_ms"]) for r in records) if records else float("inf")
        return success_rate, latency, failures, consecutive_failures
    def plan(self, task_class: str, candidate_routes: list[str]) -> dict:
        ranked = []
        reason_codes = []
        for route in sorted(set(candidate_routes)):
            success_rate, latency, failures, consecutive = self._route_stats(task_class, route)
            abandoned = consecutive >= self.failure_threshold and failures > 0
            if abandoned:
                reason_codes.append("route_abandoned")
                continue
            ranked.append(
                {
                    "route": route,
                    "success_rate": success_rate,
                    "latency_ms": latency,
                    "failures": failures,
                }
            )
        if not ranked:
            return {
                "selected_route": None,
                "ranked_routes": [],
                "reason_codes": ["all_routes_abandoned"],
                "policy_fingerprint": self._fingerprint({"task_class": task_class}),
            }
        ranked.sort(key=lambda r: (-r["success_rate"], r["latency_ms"], r["route"]))
        selected = ranked[0]["route"]
        return {
            "selected_route": selected,
            "ranked_routes": ranked,
            "reason_codes": sorted(set(reason_codes)) or ["evidence_ranked"],
            "policy_fingerprint": self._fingerprint(
                {"task_class": task_class, "ranked_routes": ranked, "selected_route": selected}
            ),
        }
    def route_health(self, task_class: str, candidate_routes: list[str]) -> dict:
        """Project route evidence into a read-only operational health snapshot."""
        routes = {}
        for route in sorted(set(candidate_routes)):
            success_rate, latency, failures, consecutive = self._route_stats(task_class, route)
            routes[route] = {
                "success_rate": round(success_rate, 6),
                "mean_latency_ms": None if latency == float("inf") else round(latency, 3),
                "failures": failures,
                "consecutive_failures": consecutive,
                "abandoned": consecutive >= self.failure_threshold and failures > 0,
            }
        snapshot = {
            "task_class": str(task_class),
            "failure_threshold": self.failure_threshold,
            "routes": routes,
        }
        snapshot["snapshot_fingerprint"] = self._fingerprint(snapshot)
        snapshot["generated_at"] = datetime.now(timezone.utc).isoformat()
        return snapshot

    def write_route_health(
        self, output_path: str | Path, task_class: str, candidate_routes: list[str]
    ) -> dict:
        """Persist the health projection without modifying execution evidence."""
        snapshot = self.route_health(task_class, candidate_routes)
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp = destination.with_suffix(destination.suffix + ".tmp")
        temp.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
        temp.replace(destination)
        return snapshot
