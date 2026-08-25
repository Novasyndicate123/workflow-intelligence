from __future__ import annotations


class ReviewDecisionPacket:
    """Build a non-executing, provenance-bound human review packet."""

    def __init__(self, review_queue):
        self.review_queue = review_queue

    def build(self, response_id: str) -> dict:
        record = self.review_queue._latest(response_id)
        if record is None:
            raise ValueError("response_not_queued")
        if record.get("status") != "PENDING":
            raise ValueError("response_not_pending")

        return {
            "status": "READY_FOR_REVIEW",
            "review_id": record.get("review_id"),
            "response_id": record.get("response_id"),
            "source_fingerprint": record.get("source_fingerprint"),
            "classification": record.get("classification"),
            "evidence_score": record.get("evidence_score", 0.0),
            "consent": bool(record.get("consent")),
            "review_required": True,
            "recommended_actions": ["REVIEWED", "REJECTED", "PROMOTE"],
            "promote_now": False,
            "execution_authorized": False,
            "external_send_authorized": False,
            "revenue_verified": False,
        }
