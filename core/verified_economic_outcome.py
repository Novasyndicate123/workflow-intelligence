from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class VerifiedEconomicOutcome:
    """Canonical immutable record of a verified economic outcome."""

    def __init__(self, path="results/verified_economic_outcomes.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _fingerprint(payload):
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def record(self, *, workflow_id, transaction, fulfillment, revenue, metrics,
               lineage, origin_stage, origin_id):
        if transaction.get("status") != "paid" or transaction.get("payment_status") != "paid" or not transaction.get("sale_confirmed"):
            raise ValueError("verified_payment_required")
        if fulfillment.get("workflow_id") != workflow_id or fulfillment.get("stage") != "outcome_recorded":
            raise ValueError("fulfillment_outcome_required")
        amount = float(revenue.get("verified_revenue_value", 0) or 0)
        if amount <= 0 or not revenue.get("evidence_reference"):
            raise ValueError("verified_revenue_required")
        trace = lineage.trace_from(origin_stage, origin_id)
        if trace.get("status") != "complete":
            raise ValueError("complete_lineage_required")
        trace = dict(trace)
        trace["links"] = [
            {
                "source_stage": link.source_stage,
                "source_id": link.source_id,
                "target_stage": link.target_stage,
                "target_id": link.target_id,
                "evidence_status": link.evidence_status,
            }
            for link in trace.get("links", [])
        ]
        outcome_id = str(fulfillment.get("outcome_id") or trace.get("terminal_id"))
        payload = {
            "workflow_id": str(workflow_id),
            "transaction_id": str(transaction["transaction_id"]),
            "outcome_id": outcome_id,
            "verified_revenue_value": amount,
            "currency": str(revenue.get("currency", "AUD")).upper(),
            "evidence_reference": str(revenue["evidence_reference"]),
            "metrics": dict(metrics or {}),
            "lineage": trace,
        }
        payload["record_id"] = uuid.uuid4().hex
        payload["recorded_at"] = datetime.now(timezone.utc).isoformat()
        payload["status"] = "VERIFIED_ECONOMIC_OUTCOME"
        payload["learning_eligible"] = True
        payload["immutable"] = True
        if any(row.get("workflow_id") == workflow_id for row in self.records()):
            raise ValueError("economic_outcome_already_verified")
        payload["fingerprint"] = self._fingerprint(payload)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
        return payload

    def records(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    @classmethod
    def verify_record(cls, record):
        if not record or record.get("immutable") is not True:
            return False
        fingerprint = record.get("fingerprint")
        if not fingerprint:
            return False
        body = dict(record)
        body.pop("fingerprint", None)
        return fingerprint == cls._fingerprint(body)
