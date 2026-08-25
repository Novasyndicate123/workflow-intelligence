from core.economic_experiment_decision import EconomicExperimentDecision
from core.prioritized_candidates import prioritize_with_verified_outcomes


def _record(net_value):
    record = {
        "record_id": "economic-001",
        "status": "VERIFIED_ECONOMIC_OUTCOME",
        "learning_eligible": True,
        "verified_revenue_value": 2000.0,
        "metrics": {"net_value": net_value},
        "immutable": True,
    }
    from core.verified_economic_outcome import VerifiedEconomicOutcome
    record["fingerprint"] = VerifiedEconomicOutcome._fingerprint(record)
    return record


def test_positive_verified_outcome_surfaces_continue_decision_without_authority():
    proposals = [{"id": "cand-1", "expected_upside": .6, "evidence_strength": .2,
                  "uncertainty": .2, "implementation_cost": .2, "risk": .1}]
    result = prioritize_with_verified_outcomes(proposals, {"cand-1": _record(1400)})
    row = result["ranked"][0]
    decision = EconomicExperimentDecision().decide(_record(1400))
    assert decision["decision"] == "CONTINUE_BOUNDED_EXPERIMENT"
    assert row["lineage"]["gate"] == "verified_economic_outcome"
    assert row["execution_authorized"] is False


def test_negative_verified_outcome_surfaces_kill_decision_without_mutating_ranking():
    decision = EconomicExperimentDecision().decide(_record(-1))
    assert decision["decision"] == "KILL"
    assert decision["execution_authorized"] is False
