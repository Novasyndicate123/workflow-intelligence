from core.acquisition_review_handoff import AcquisitionReviewHandoff


def test_build_handoff_normalizes_review_fields_and_blocks_external_action():
    source = {
        "opportunity_id": "opp-1",
        "source": "Business Victoria",
        "opportunity_type": "free_webinar",
        "context": "SMB workflow/AI session",
        "current_as_of": "2026-08-25",
        "fit_score": 0.92,
    }
    result = AcquisitionReviewHandoff().build(source)
    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["opportunity_id"] == "opp-1"
    assert result["observation_only"] is True
    assert result["human_review_required"] is True
    assert result["external_send_authorized"] is False
    assert result["execution_authorized"] is False
    assert result["evidence_promotion_authorized"] is False
    assert result["what_counts_as_evidence"]
    assert result["what_does_not_count"]


def test_build_handoff_rejects_missing_identity():
    try:
        AcquisitionReviewHandoff().build({"source": "x"})
    except ValueError as exc:
        assert str(exc) == "opportunity_id_required"
    else:
        raise AssertionError("expected ValueError")
