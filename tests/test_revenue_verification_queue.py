from core.pilot_candidate_queue import build_pilot_candidate_queue
from core.pilot_candidate_queue_report import render_pilot_candidate_queue


def test_candidate_queue_uses_verified_revenue_ledger():
    requests = [{
        "workflow_id": "wf-1",
        "stage": "pilot_candidate",
        "revenue_verified": False,
        "timestamp": "2026-08-25T08:00:00+00:00",
    }]
    ledger = [{
        "workflow_id": "wf-1",
        "event": "revenue_verified",
        "verified_revenue_value": 1500,
        "currency": "AUD",
    }]
    row = build_pilot_candidate_queue(
        requests, [], verification=ledger, now="2026-08-25T10:00:00+00:00"
    )[0]
    assert row["revenue_verified"] is True
    assert row["next_action"] == "recorded_revenue_followup"


def test_candidate_queue_report_exposes_human_revenue_verification_control():
    html = render_pilot_candidate_queue([{
        "workflow_id": "wf-1",
        "market": "english_worldwide",
        "geography": "global",
        "fulfillment_stage": "outcome_recorded",
        "age_hours": 2,
        "revenue_verified": False,
        "followup_status": "none",
        "next_action": "verify_outcome",
    }])
    assert "Verify revenue" in html
    assert "evidence_reference" in html
