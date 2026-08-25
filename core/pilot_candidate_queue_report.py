from __future__ import annotations

from html import escape


def render_pilot_candidate_queue(rows: list[dict]) -> str:
    cards = []
    for row in rows:
        workflow_id = escape(row.get("workflow_id", ""))
        market = escape(row.get("market", "english_worldwide"))
        geography = escape(row.get("geography", "global"))
        stage = escape(row.get("fulfillment_stage", "not_started"))
        age = escape(str(row.get("age_hours", "unknown")))
        action = escape(row.get("next_action", "review_and_scope"))
        followup_status = escape(row.get("followup_status", "none"))
        verified = "Yes" if row.get("revenue_verified") else "No"
        cards.append(
            f"<article class='card'><strong>{workflow_id}</strong> · {market} · {geography}"
            f"<p>Fulfillment: {stage} · Age: {age}h · Verified revenue: {verified}</p>"
            f"<p>Follow-up: <strong>{followup_status}</strong> · Next action: <strong>{action}</strong></p>"
            f"<form method='post' action='/operator/pilot-candidates/action'><input type='hidden' name='workflow_id' value='{workflow_id}'><input type='hidden' name='action' value='schedule_followup'><input name='operator_id' placeholder='Operator ID' required><input name='scheduled_for' placeholder='2026-08-26T10:00:00+00:00' required><button type='submit'>Schedule follow-up</button></form>"
            f"<form method='post' action='/operator/pilot-candidates/action'><input type='hidden' name='workflow_id' value='{workflow_id}'><input type='hidden' name='action' value='verify_revenue'><input name='operator_id' placeholder='Operator ID' required><input name='verified_revenue_value' type='number' min='0.01' step='0.01' placeholder='AUD amount' required><input name='evidence_reference' placeholder='Evidence reference' required><button type='submit'>Verify revenue</button></form></article>"
        )
    return """<!doctype html><html><head><meta charset='utf-8'><title>Workflow Intelligence · Pilot Candidate Queue</title>
<style>body{font-family:system-ui;margin:40px;background:#f5f5f2;color:#111}main{max-width:900px;margin:auto}.card{background:#fff;border:1px solid #ddd;padding:20px;margin:14px 0}.card p{color:#475467;margin:7px 0}.card form{display:inline-block;margin:6px 8px 0 0}.card input,.card button{padding:7px;margin-right:5px}</style>
</head><body><main><h1>Pilot candidate queue</h1><p>Private operator view. Contact details and raw workflow text are intentionally excluded.</p>""" + ("".join(cards) or "<p>No pilot candidates.</p>") + "</main></body></html>"
