import pytest

from core.review_decision_packet import ReviewDecisionPacket


def test_build_packet_for_pending_review():
    queue = type("Queue", (), {"_latest": lambda self, rid: {
        "response_id": rid,
        "source_fingerprint": "abc123",
        "classification": "offer_requested",
        "evidence_score": 0.8,
        "consent": True,
        "status": "PENDING",
        "promoted": False,
        "reviewer_id": None,
        "reason": None,
    }})()
    packet = ReviewDecisionPacket(queue).build("resp-1")
    assert packet["status"] == "READY_FOR_REVIEW"
    assert packet["response_id"] == "resp-1"
    assert packet["review_required"] is True
    assert packet["recommended_actions"] == ["REVIEWED", "REJECTED", "PROMOTE"]


def test_packet_is_non_executing_and_provenance_bound():
    queue = type("Queue", (), {"_latest": lambda self, rid: {
        "response_id": rid,
        "source_fingerprint": "fp-9",
        "classification": "problem_confirmed",
        "evidence_score": 0.6,
        "consent": True,
        "status": "PENDING",
        "promoted": False,
    }})()
    packet = ReviewDecisionPacket(queue).build("resp-9")
    assert packet["source_fingerprint"] == "fp-9"
    assert packet["promote_now"] is False
    assert packet["execution_authorized"] is False
    assert packet["external_send_authorized"] is False
    assert packet["revenue_verified"] is False


def test_missing_or_already_reviewed_response_rejected():
    missing = type("Queue", (), {"_latest": lambda self, rid: None})()
    with pytest.raises(ValueError, match="response_not_queued"):
        ReviewDecisionPacket(missing).build("missing")

    reviewed = type("Queue", (), {"_latest": lambda self, rid: {
        "response_id": rid,
        "status": "PROMOTED",
    }})()
    with pytest.raises(ValueError, match="response_not_pending"):
        ReviewDecisionPacket(reviewed).build("done")
