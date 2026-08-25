from __future__ import annotations

import hashlib
import json


class PromotedEvidenceExperimentPlanner:
    """Create bounded DRAFT plans from human-promoted response evidence."""

    def __init__(self, review_queue):
        self.review_queue = review_queue

    @staticmethod
    def _fingerprint(record: dict) -> str:
        body = {k: v for k, v in record.items() if k != "record_fingerprint"}
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def plan(self, opportunity_id: str, response_id: str) -> dict:
        record = self.review_queue._latest(response_id)
        if record is None or record.get("status") != "PROMOTED":
            raise ValueError("promoted_response_required")
        if self._fingerprint(record) != record.get("record_fingerprint"):
            raise ValueError("invalid_review_integrity")
        return {
            "status": "DRAFT",
            "opportunity_id": str(opportunity_id),
            "human_approval_required": True,
            "execution_authorized": False,
            "external_send_authorized": False,
            "revenue_verified": False,
            "economic_outcome_verified": False,
            "provenance": {
                "response_id": str(response_id),
                "source_fingerprint": record["source_fingerprint"],
                "review_fingerprint": record["record_fingerprint"],
            },
            "evidence_score": float(record.get("evidence_score", 0.0)),
            "next_experiment": "Validate the bounded SMB workflow-audit offer with the reviewed customer signal.",
        }
