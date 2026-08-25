import pytest

from core.smb_response_evidence import SMBResponseEvidenceStore
from core.smb_response_review import SMBResponseReviewQueue


def test_placeholder_note_rejected_at_ingestion(tmp_path):
    store = SMBResponseEvidenceStore(tmp_path / "responses.jsonl")
    with pytest.raises(ValueError, match="placeholder_note_not_allowed"):
        store.record("run-1", "problem_confirmed", "ACTUAL CUSTOMER RESPONSE HERE", True, "manual_review")


def test_existing_placeholder_record_cannot_enter_review(tmp_path):
    path = tmp_path / "responses.jsonl"
    path.write_text('{"response_id":"r1","fingerprint":"fp","classification":"problem_confirmed","note":"ACTUAL CUSTOMER RESPONSE HERE","consent":true,"experiment_run_id":"run-1","evidence_score":0.6}\n', encoding="utf-8")
    store = SMBResponseEvidenceStore(path)
    row = store.records()[0]
    queue = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    with pytest.raises(ValueError, match="placeholder_note_not_allowed"):
        queue.submit(row)


def test_instruction_placeholder_variants_rejected(tmp_path):
    store = SMBResponseEvidenceStore(tmp_path / "responses.jsonl")
    variants = [
        "EXACT CUSTOMER WORDS HERE",
        "PASTE CUSTOMER RESPONSE HERE",
        "PASTE THE CUSTOMER RESPONSE HERE",
        "CUSTOMER RESPONSE GOES HERE",
    ]
    for note in variants:
        with pytest.raises(ValueError, match="placeholder_note_not_allowed"):
            store.record("run-1", "problem_confirmed", note, True, "manual_review")
