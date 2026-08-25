import json
import pytest
from datetime import datetime, timezone
from core.smb_response_evidence import SMBResponseEvidenceStore


def test_append_and_read_response(tmp_path):
    store = SMBResponseEvidenceStore(tmp_path / "responses.jsonl")
    row = store.record("run-1", "problem_confirmed", "Manual quoting takes hours", True, "business_community")
    assert row["experiment_run_id"] == "run-1"
    assert row["classification"] == "problem_confirmed"
    assert row["evidence_score"] > 0
    assert store.records()[0]["fingerprint"] == row["fingerprint"]


def test_duplicate_response_id_rejected(tmp_path):
    store = SMBResponseEvidenceStore(tmp_path / "responses.jsonl")
    first = store.record("run-1", "offer_requested", "Send me the details", True, "business_community", response_id="r1")
    assert first["response_id"] == "r1"
    with pytest.raises(ValueError, match="duplicate_response_id"):
        store.record("run-1", "offer_requested", "Send me the details", True, "business_community", response_id="r1")


def test_invalid_classification_and_empty_note_rejected(tmp_path):
    store = SMBResponseEvidenceStore(tmp_path / "responses.jsonl")
    with pytest.raises(ValueError, match="invalid_classification"):
        store.record("run-1", "maybe", "note", True, "community")
    with pytest.raises(ValueError, match="note_required"):
        store.record("run-1", "unclear", "", True, "community")
