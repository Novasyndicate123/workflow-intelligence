from __future__ import annotations

from .bounded_experiment_plan import BoundedExperimentPlan


class EconomicExperimentDecision:
    """Translate verified economic outcomes into bounded experiment decisions."""

    def decide(self, outcome: dict, *, candidate_id=None, hypothesis=None) -> dict:
        if outcome.get("status") != "VERIFIED_ECONOMIC_OUTCOME" or outcome.get("learning_eligible") is not True:
            raise ValueError("verified_economic_outcome_required")
        revenue = float(outcome.get("verified_revenue_value", 0.0) or 0.0)
        net_value = float((outcome.get("metrics") or {}).get("net_value", 0.0) or 0.0)
        if revenue <= 0.0:
            raise ValueError("verified_revenue_required")
        margin = max(0.0, min(1.0, net_value / revenue))
        if net_value <= 0.0:
            decision, action = "KILL", "retire_candidate"
        else:
            decision, action = "CONTINUE_BOUNDED_EXPERIMENT", "run_next_bounded_experiment"
        result = {
            "decision": decision,
            "next_action": action,
            "learning_confidence": round(margin, 4),
            "execution_authorized": False,
            "promotion_authorized": False,
            "economic_value": net_value,
        }
        if decision == "CONTINUE_BOUNDED_EXPERIMENT" and candidate_id and hypothesis:
            plan_decision = {"decision": decision, "learning_multiplier": margin, "verified": True}
            result["next_experiment_plan"] = BoundedExperimentPlan.from_decision(
                plan_decision, candidate_id=candidate_id, hypothesis=hypothesis
            )
        return result
