import pytest

from core.economic_experiment_decision import EconomicExperimentDecision


def test_verified_positive_outcome_recommends_bounded_next_experiment():
    decision = EconomicExperimentDecision().decide({
        "status": "VERIFIED_ECONOMIC_OUTCOME",
        "learning_eligible": True,
        "verified_revenue_value": 2000,
        "metrics": {"net_value": 1400, "success_rate": 1.0},
    })
    assert decision["decision"] == "CONTINUE_BOUNDED_EXPERIMENT"
    assert decision["next_action"] == "run_next_bounded_experiment"
    assert decision["execution_authorized"] is False


def test_zero_or_negative_net_value_recommends_kill():
    decision = EconomicExperimentDecision().decide({
        "status": "VERIFIED_ECONOMIC_OUTCOME",
        "learning_eligible": True,
        "verified_revenue_value": 1000,
        "metrics": {"net_value": 0},
    })
    assert decision["decision"] == "KILL"
    assert decision["next_action"] == "retire_candidate"


def test_unverified_economic_result_cannot_change_policy():
    with pytest.raises(ValueError, match="verified_economic_outcome_required"):
        EconomicExperimentDecision().decide({
            "status": "PENDING",
            "learning_eligible": False,
            "verified_revenue_value": 500,
            "metrics": {"net_value": 400},
        })


def test_high_value_outcome_increases_learning_confidence_but_not_authority():
    decision = EconomicExperimentDecision().decide({
        "status": "VERIFIED_ECONOMIC_OUTCOME",
        "learning_eligible": True,
        "verified_revenue_value": 10000,
        "metrics": {"net_value": 9000},
    })
    assert decision["learning_confidence"] == 0.9
    assert decision["execution_authorized"] is False
    assert decision["promotion_authorized"] is False
