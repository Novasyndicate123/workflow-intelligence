from core.economic_experiment_decision import EconomicExperimentDecision


def test_continue_decision_can_emit_bounded_plan():
    decision = EconomicExperimentDecision().decide(
        {"status": "VERIFIED_ECONOMIC_OUTCOME", "learning_eligible": True,
         "verified_revenue_value": 1500, "metrics": {"net_value": 1200}},
        candidate_id="cand-1",
        hypothesis="Improve qualified buyer conversion",
    )
    plan = decision["next_experiment_plan"]
    assert plan["status"] == "DRAFT"
    assert plan["human_approval_required"] is True
    assert plan["execution_authorized"] is False
