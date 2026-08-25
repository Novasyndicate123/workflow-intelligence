from __future__ import annotations


class AcquisitionReviewHandoff:
    """Build a review-only acquisition handoff without side effects."""

    def build(self, opportunity: dict) -> dict:
        opportunity_id = str(opportunity.get("opportunity_id", "")).strip()
        if not opportunity_id:
            raise ValueError("opportunity_id_required")

        return {
            "status": "READY_FOR_HUMAN_REVIEW",
            "opportunity_id": opportunity_id,
            "source": opportunity.get("source", ""),
            "opportunity_type": opportunity.get("opportunity_type", ""),
            "context": opportunity.get("context", ""),
            "current_as_of": opportunity.get("current_as_of", ""),
            "fit_score": opportunity.get("fit_score"),
            "observation_only": True,
            "human_review_required": True,
            "external_send_authorized": False,
            "execution_authorized": False,
            "evidence_promotion_authorized": False,
            "what_counts_as_evidence": [
                "A genuine statement or response from an actual business participant.",
                "A concrete workflow problem described by that participant.",
                "An explicit request to evaluate the proposed offer or pilot.",
            ],
            "what_does_not_count": [
                "Event attendance, page views, or general market interest.",
                "Third-party claims about an individual business problem.",
                "Templates, placeholders, inferred demand, or synthetic responses.",
            ],
        }
