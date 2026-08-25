from __future__ import annotations

import hashlib
import json


class PromotedResponseOpportunityBridge:
    """Apply only human-promoted, intact response evidence to opportunity scoring."""

    def __init__(self, review_queue):
        self.review_queue = review_queue

    @staticmethod
    def _record_fingerprint(record: dict) -> str:
        body = {k: v for k, v in record.items() if k != "record_fingerprint"}
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _latest_promoted(self, response_id: str) -> dict:
        record = self.review_queue._latest(response_id)
        if record is None or record.get("status") != "PROMOTED":
            raise ValueError("promoted_response_required")
        expected = self._record_fingerprint(record)
        if expected != record.get("record_fingerprint"):
            raise ValueError("invalid_review_integrity")
        if not record.get("promoted"):
            raise ValueError("promoted_response_required")
        return record

    def apply(self, opportunity: dict, response_id: str) -> dict:
        record = self._latest_promoted(response_id)
        current = float(opportunity.get("evidence_confidence", 0.0) or 0.0)
        boost = min(0.10, max(0.0, float(record.get("evidence_score", 0.0)) * 0.10))
        updated = dict(opportunity)
        updated["evidence_confidence"] = round(min(1.0, current + boost), 6)
        updated["revenue_verified"] = False
        updated["execution_authorized"] = False
        updated["promotion_source_response_id"] = response_id
        updated["promotion_source_fingerprint"] = record["record_fingerprint"]
        updated["status"] = "PROMOTED_EVIDENCE_APPLIED"
        return updated
