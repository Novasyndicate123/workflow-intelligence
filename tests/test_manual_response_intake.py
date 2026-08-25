import pytest
from core.manual_response_intake import ManualResponseIntake
from core.smb_response_evidence import SMBResponseEvidenceStore


def make(tmp_path):
    store = SMBResponseEvidenceStore(tmp_path / "evidence.jsonl")
    return ManualResponseIntake(store)


def test_intake_records_one_response(tmp_path):
    intake = make(tmp_path)
    result = intake.record("run-1", "problem_confirmed", "Manual triage is slowing us down.", True, "human_notes")
    assert result["status"] == "RECORDED"
    assert result["response_id"]
    assert result["fingerprint"]
    assert result["evidence_score"] > 0


def test_intake_rejects_missing_run_id(tmp_path):
    with pytest.raises(ValueError, match="experiment_run_id_required"):
        make(tmp_path).record("", "problem_confirmed", "Issue confirmed.", True, "human_notes")


def test_intake_rejects_empty_note_and_source(tmp_path):
    with pytest.raises(ValueError, match="note_required"):
        make(tmp_path).record("run-1", "problem_confirmed", "", True, "human_notes")
    with pytest.raises(ValueError, match="source_channel_required"):
        make(tmp_path).record("run-1", "problem_confirmed", "Issue confirmed.", True, "")


def test_intake_never_promotes(tmp_path):
    result = make(tmp_path).record("run-1", "pilot_interest", "Please show the audit process.", True, "human_notes")
    assert result["promoted"] is False
    assert result["execution_authorized"] is False
    assert result["external_send_authorized"] is False
