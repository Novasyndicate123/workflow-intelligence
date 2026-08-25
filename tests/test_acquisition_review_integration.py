import pytest

from core.acquisition_review_integration import AcquisitionReviewIntegration
from core.smb_response_evidence import SMBResponseEvidenceStore
from core.smb_response_review import SMBResponseReviewQueue


def make(tmp_path):
    evidence = SMBResponseEvidenceStore(tmp_path / "evidence.jsonl")
    reviews = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    return AcquisitionReviewIntegration(evidence, reviews)


def test_handoff_creates_review_target_without_escalation(tmp_path):
    integration = make(tmp_path)
    handoff = {
        "status": "READY_FOR_HUMAN_REVIEW",
        "opportunity_id": "opp-1",
        "source": "business_victoria",
        "context": "free small-business session",
        "observation_only": True,
        "human_review_required": True,
        "external_send_authorized": False,
        "execution_authorized": False,
        "evidence_promotion_authorized": False,
    }
    result = integration.prepare_response_capture(handoff, experiment_run_id="run-1")
    assert result["status"] == "READY_FOR_RESPONSE_CAPTURE"
    assert result["opportunity_id"] == "opp-1"
    assert result["experiment_run_id"] == "run-1"
    assert result["human_review_required"] is True
    assert result["external_send_authorized"] is False
    assert result["execution_authorized"] is False
    assert result["evidence_promotion_authorized"] is False


def test_record_real_response_into_review_queue(tmp_path):
    integration = make(tmp_path)
    result = integration.record_and_queue(
        experiment_run_id="run-1",
        classification="problem_confirmed",
        note="Our manual triage is taking too much time.",
        consent=True,
        source_channel="human_review",
    )
    assert result["status"] == "QUEUED_FOR_HUMAN_REVIEW"
    assert result["promoted"] is False
    assert result["execution_authorized"] is False
    assert result["external_send_authorized"] is False
    assert result["review_id"]


def test_placeholder_response_never_reaches_review(tmp_path):
    with pytest.raises(ValueError, match="placeholder_note_not_allowed"):
        make(tmp_path).record_and_queue(
            experiment_run_id="run-1",
            classification="problem_confirmed",
            note="EXACT CUSTOMER WORDS HERE",
            consent=True,
            source_channel="human_review",
        )
