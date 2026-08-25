import pytest

from core.promoted_response_opportunity_bridge import PromotedResponseOpportunityBridge
from core.smb_response_evidence import SMBResponseEvidenceStore
from core.smb_response_review import SMBResponseReviewQueue
from core.promoted_evidence_experiment_planner import PromotedEvidenceExperimentPlanner


def _promoted(tmp_path):
    evidence = SMBResponseEvidenceStore(tmp_path / "evidence.jsonl")
    row = evidence.record("run-1", "pilot_interest", "Customer wants a scoped pilot.", True, "manual")
    review = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    review.submit(row)
    promoted = review.review(row["response_id"], reviewer_id="op", action="PROMOTE", reason="Explicit pilot interest.")
    return promoted, review


def test_promoted_signal_creates_bounded_next_experiment(tmp_path):
    promoted, review = _promoted(tmp_path)
    planner = PromotedEvidenceExperimentPlanner(review)
    plan = planner.plan("smb-workflow-audit", promoted["response_id"])
    assert plan["status"] == "DRAFT"
    assert plan["human_approval_required"] is True
    assert plan["execution_authorized"] is False
    assert plan["external_send_authorized"] is False


def test_unpromoted_signal_is_rejected(tmp_path):
    evidence = SMBResponseEvidenceStore(tmp_path / "evidence.jsonl")
    row = evidence.record("run-1", "problem_confirmed", "Recurring workflow pain.", True, "manual")
    review = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    review.submit(row)
    planner = PromotedEvidenceExperimentPlanner(review)
    with pytest.raises(ValueError, match="promoted_response_required"):
        planner.plan("smb-workflow-audit", row["response_id"])


def test_planner_does_not_create_revenue_truth(tmp_path):
    promoted, review = _promoted(tmp_path)
    planner = PromotedEvidenceExperimentPlanner(review)
    plan = planner.plan("smb-workflow-audit", promoted["response_id"])
    assert plan["revenue_verified"] is False
    assert plan["economic_outcome_verified"] is False
