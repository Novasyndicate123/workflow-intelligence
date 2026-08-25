import pytest
from core.operator_response_console import OperatorResponseConsole


def test_console_records_manual_response(tmp_path):
    console = OperatorResponseConsole(results_path=tmp_path / "evidence.jsonl")
    result = console.record(
        experiment_run_id="run-1",
        classification="problem_confirmed",
        note="Manual customer reply confirmed recurring workflow friction.",
        consent=True,
        source_channel="manual_email",
    )
    assert result["status"] == "RECORDED"
    assert result["promoted"] is False
    assert result["execution_authorized"] is False


def test_console_rejects_invalid_classification(tmp_path):
    console = OperatorResponseConsole(results_path=tmp_path / "evidence.jsonl")
    with pytest.raises(ValueError, match="invalid_classification"):
        console.record("run-1", "invalid", "note", True, "manual")


def test_console_never_grants_external_authority(tmp_path):
    console = OperatorResponseConsole(results_path=tmp_path / "evidence.jsonl")
    result = console.record("run-1", "pilot_interest", "Customer requested a pilot discussion.", True, "manual")
    assert result["external_send_authorized"] is False
    assert result["revenue_verified"] is False
    assert result["economic_outcome_verified"] is False
