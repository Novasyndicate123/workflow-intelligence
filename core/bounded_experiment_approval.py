from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .operator_access import operator_token_valid


class BoundedExperimentApproval:
    """Durable human approval/rejection gate for bounded experiment plans."""

    def __init__(self, path="results/bounded_experiment_approvals.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _fingerprint(plan: dict) -> str:
        body = json.dumps(plan, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(body.encode("utf-8")).hexdigest()

    def _records(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def decide(self, plan, *, presented_token, configured_token, operator_id, action, reason=None):
        if not operator_token_valid(presented_token, configured_token):
            return None
        if plan.get("status") != "DRAFT":
            raise ValueError("draft_plan_required")
        action = str(action or "").upper()
        if action not in {"APPROVE", "REJECT"}:
            raise ValueError("invalid_approval_action")
        fingerprint = self._fingerprint(plan)
        if any(row.get("plan_fingerprint") == fingerprint or row.get("candidate_id") == plan.get("candidate_id") for row in self._records()):
            raise ValueError("approval_already_decided")
        record = {
            "record_id": uuid.uuid4().hex,
            "plan_fingerprint": fingerprint,
            "candidate_id": str(plan.get("candidate_id")),
            "status": "APPROVED" if action == "APPROVE" else "REJECTED",
            "operator_id": str(operator_id or ""),
            "reason": str(reason or "") if action == "REJECT" else None,
            "decided_at": datetime.now(timezone.utc).isoformat(),
            "plan": dict(plan),
            "execution_authorized": False,
            "external_send_authorized": False,
            "immutable": True,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    def records(self):
        return self._records()
