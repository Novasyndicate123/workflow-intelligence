from __future__ import annotations

from datetime import datetime, timezone


class BoundedExperimentPlan:
    """Create human-reviewable experiment plans without execution authority."""

    @classmethod
    def from_decision(cls, decision: dict, *, candidate_id: str, hypothesis: str) -> dict:
        if decision.get("verified") is False:
            raise ValueError("verified_decision_required")
        if decision.get("decision") != "CONTINUE_BOUNDED_EXPERIMENT":
            raise ValueError("experiment_not_allowed_after_kill")
        multiplier = float(decision.get("learning_multiplier", 0.0) or 0.0)
        if not 0.0 < multiplier <= 1.0:
            raise ValueError("valid_learning_multiplier_required")
        if not candidate_id or not hypothesis:
            raise ValueError("candidate_and_hypothesis_required")
        return {
            "status": "DRAFT",
            "candidate_id": str(candidate_id),
            "hypothesis": str(hypothesis),
            "learning_multiplier": multiplier,
            "max_scope": "single_bounded_experiment",
            "human_approval_required": True,
            "external_send_authorized": False,
            "execution_authorized": False,
            "success_metric": "verified_economic_outcome",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
