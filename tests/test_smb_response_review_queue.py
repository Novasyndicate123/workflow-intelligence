import json
from pathlib import Path

import pytest

from core.smb_response_evidence import SMBResponseEvidenceStore
from core.smb_response_review import SMBResponseReviewQueue


def _seed(tmp_path: Path):
    store = SMBResponseEvidenceStore(tmp_path / "responses.jsonl")
    row = store.record(
        experiment_run_id="78fa7486907c4da8b851a8e01a729f58",
        classification="problem_confirmed",
        note="Manual invoice review consumes too much time.",
        consent=True,
        source_channel="human_contact",
    )
    return store, row


def test_review_starts_pending_and_preserves_source_fingerprint(tmp_path):
    _, row = _seed(tmp_path)
    queue = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    item = queue.submit(row)
    assert item["status"] == "PENDING"
    assert item["source_fingerprint"] == row["fingerprint"]
    assert item["promoted"] is False


def test_promote_requires_consent_and_explicit_reviewer(tmp_path):
    _, row = _seed(tmp_path)
    queue = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    queue.submit(row)
    approved = queue.review(row["response_id"], reviewer_id="operator", action="PROMOTE", reason="Clear qualified pain signal.")
    assert approved["status"] == "PROMOTED"
    assert approved["promoted"] is True
    assert approved["reviewer_id"] == "operator"


def test_unconsented_response_cannot_promote(tmp_path):
    store = SMBResponseEvidenceStore(tmp_path / "responses.jsonl")
    row = store.record(
        experiment_run_id="run-2",
        classification="pilot_interest",
        note="Interested in hearing more.",
        consent=False,
        source_channel="human_contact",
    )
    queue = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    queue.submit(row)
    with pytest.raises(ValueError, match="consent_required"):
        queue.review(row["response_id"], reviewer_id="operator", action="PROMOTE", reason="Needs follow-up.")


def test_duplicate_review_is_rejected(tmp_path):
    _, row = _seed(tmp_path)
    queue = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    queue.submit(row)
    queue.review(row["response_id"], reviewer_id="operator", action="REVIEWED", reason="Reviewed manually.")
    with pytest.raises(ValueError, match="already_reviewed"):
        queue.review(row["response_id"], reviewer_id="operator", action="REJECTED", reason="Changed mind.")
