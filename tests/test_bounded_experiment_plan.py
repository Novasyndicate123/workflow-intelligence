import pytest

from core.bounded_experiment_plan import BoundedExperimentPlan


def test_continue_decision_emits_human_reviewable_plan():
    plan = BoundedExperimentPlan.from_decision(
        {"decision": "CONTINUE_BOUNDED_EXPERIMENT", "learning_multiplier": 0.8},
        candidate_id="cand-1",
        hypothesis="Improve qualified buyer conversion",
    )
    assert plan["status"] == "DRAFT"
    assert plan["candidate_id"] == "cand-1"
    assert plan["max_scope"] == "single_bounded_experiment"
    assert plan["human_approval_required"] is True
    assert plan["external_send_authorized"] is False
    assert plan["success_metric"] == "verified_economic_outcome"


def test_kill_decision_refuses_experiment_plan():
    with pytest.raises(ValueError, match="experiment_not_allowed_after_kill"):
        BoundedExperimentPlan.from_decision(
            {"decision": "KILL", "learning_multiplier": 0.1},
            candidate_id="cand-2",
            hypothesis="Try again",
        )


def test_plan_requires_verified_decision():
    with pytest.raises(ValueError, match="verified_decision_required"):
        BoundedExperimentPlan.from_decision(
            {"decision": "CONTINUE_BOUNDED_EXPERIMENT", "learning_multiplier": 0.8, "verified": False},
            candidate_id="cand-3",
            hypothesis="Test",
        )


def test_plan_is_not_execution_authority():
    plan = BoundedExperimentPlan.from_decision(
        {"decision": "CONTINUE_BOUNDED_EXPERIMENT", "learning_multiplier": 0.9},
        candidate_id="cand-4",
        hypothesis="Test",
    )
    assert plan["execution_authorized"] is False
