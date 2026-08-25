from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .bounded_experiment_approval import BoundedExperimentApproval


class SandboxedExperimentRunner:
    """Run one approved, caller-supplied local experiment action."""

    def __init__(self, approval_path):
        self.approvals = BoundedExperimentApproval(approval_path)
        self.audit_path = Path(approval_path).with_name("bounded_experiment_runs.jsonl")
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def approve_for_test(self, plan, operator_id):
        return self.approvals.decide(
            plan,
            presented_token="test",
            configured_token="test",
            operator_id=operator_id,
            action="APPROVE",
        )

    def run(self, plan, approval_fingerprint, action):
        fingerprint = self.approvals._fingerprint(plan)
        approved = next(
            (row for row in self.approvals.records()
             if row.get("plan_fingerprint") == fingerprint
             and row.get("plan_fingerprint") == approval_fingerprint
             and row.get("status") == "APPROVED"),
            None,
        )
        if approved is None:
            raise ValueError("approved_plan_required")
        if plan.get("external_send_authorized") or plan.get("payment_authorized"):
            raise ValueError("local_action_required")
        value = action()
        if isinstance(value, str) and any(token in value.lower() for token in ("send_email", "send", "payment", "charge")):
            raise ValueError("local_action_required")
        run = {
            "run_id": uuid.uuid4().hex,
            "plan_fingerprint": approval_fingerprint,
            "candidate_id": plan.get("candidate_id"),
            "status": "completed",
            "steps": 1,
            "execution_authorized": False,
            "external_send_authorized": False,
            "evidence": value,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(run, sort_keys=True) + "\n")
        return run
