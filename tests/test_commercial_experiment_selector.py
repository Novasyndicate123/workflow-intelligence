import pytest

from core.commercial_experiment_selector import CommercialExperimentSelector


def _wedges():
    return [
        {"customer_type": "SMBs", "pain_angle": "manual processes", "offer_angle": "SMB workflow audit",
         "channel": "business communities", "success_metrics": ["3 confirmations", "1 offer request"],
         "kill_criteria": ["no qualified signal"], "budget_limit": 0.0},
        {"customer_type": "enterprises", "pain_angle": "AI scaling", "offer_angle": "AI operations assessment",
         "channel": "professional networks", "success_metrics": ["3 confirmations"],
         "kill_criteria": ["no qualified signal"], "budget_limit": 0.0},
    ]


def _validation():
    return {
        "decision": "SMB_FIRST",
        "guardrail": "No revenue is claimed until an independent real-world customer signal occurs.",
        "candidates": [
            {"rank": 1, "segment": "SMBs", "problem": "AI workflow integration", "score": 0.72,
             "validation": "TEST", "reason": "Broad need, accessible customer segment, low-cost diagnostic."},
            {"rank": 2, "segment": "Enterprises", "problem": "AI production readiness", "score": 0.74,
             "validation": "TEST-LATER", "reason": "Strong pain but longer sales cycles."},
        ],
    }


def test_selects_existing_smb_first_decision():
    packet = CommercialExperimentSelector().select(_wedges(), _validation())
    assert packet["candidate"]["customer_type"] == "SMBs"
    assert packet["approval_required"] is True
    assert packet["external_send_authorized"] is False
    assert packet["execution_authorized"] is False


def test_packet_preserves_success_and_kill_rules():
    packet = CommercialExperimentSelector().select(_wedges(), _validation())
    assert packet["success_metrics"] == ["3 confirmations", "1 offer request"]
    assert packet["kill_criteria"] == ["no qualified signal"]
    assert packet["budget_limit"] == 0.0


def test_selector_rejects_missing_validation_evidence():
    with pytest.raises(ValueError, match="commercial_validation_required"):
        CommercialExperimentSelector().select(_wedges(), {})


def test_selector_rejects_nonzero_budget_candidate():
    wedges = _wedges()
    wedges[0]["budget_limit"] = 10.0
    with pytest.raises(ValueError, match="zero_budget_required"):
        CommercialExperimentSelector().select(wedges, _validation())
