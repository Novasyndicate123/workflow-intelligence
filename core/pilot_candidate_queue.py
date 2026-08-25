from __future__ import annotations

from datetime import datetime, timezone


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)


def _followup_status(engagement: dict | None, now_dt: datetime) -> str:
    if not engagement or engagement.get("event") != "follow_up_scheduled":
        return "none"
    scheduled_for = engagement.get("scheduled_for")
    if not scheduled_for:
        return "none"
    scheduled_dt = _parse_timestamp(scheduled_for)
    if scheduled_dt > now_dt:
        return "upcoming"
    if scheduled_dt == now_dt:
        return "due"
    return "overdue"


def _next_action(request: dict, fulfillment: dict | None, engagement: dict | None = None) -> str:
    if request.get("revenue_verified") is True:
        return "recorded_revenue_followup"
    event = (engagement or {}).get("event")
    if event == "follow_up_scheduled":
        return "await_scheduled_followup"
    if event == "contacted":
        return "schedule_followup"
    stage = (fulfillment or {}).get("stage", "awaiting_human_review")
    if stage in {"awaiting_human_review", "not_started"}:
        return "review_and_scope"
    if stage == "baseline_captured":
        return "run_bounded_pilot"
    if stage == "outcome_recorded":
        return "verify_outcome"
    return "review_and_scope"


def build_pilot_candidate_queue(requests: list[dict], fulfillment: list[dict], engagement=None, verification=None, now=None) -> list[dict]:
    now_dt = _parse_timestamp(now) if now else datetime.now(timezone.utc)
    latest = {}
    for row in fulfillment:
        workflow_id = str(row.get("workflow_id", ""))
        if workflow_id:
            latest[workflow_id] = row
    latest_engagement = {}
    latest_verification = {}
    for row in (engagement or []):
        workflow_id = str(row.get("workflow_id", ""))
        if workflow_id:
            latest_engagement[workflow_id] = row
    for row in (verification or []):
        workflow_id = str(row.get("workflow_id", ""))
        if workflow_id and row.get("event") == "revenue_verified":
            latest_verification[workflow_id] = row
    rows = []
    for request in requests:
        if request.get("stage") != "pilot_candidate":
            continue
        workflow_id = str(request.get("workflow_id", ""))
        if not workflow_id:
            continue
        timestamp = request.get("timestamp")
        age_hours = round(max(0.0, (now_dt - _parse_timestamp(timestamp)).total_seconds() / 3600), 2) if timestamp else None
        row = {
            "workflow_id": workflow_id,
            "market": request.get("market", "english_worldwide"),
            "geography": request.get("geography", "global"),
            "scope_status": request.get("scope_status", "human_review_required"),
            "fulfillment_stage": (latest.get(workflow_id) or {}).get("stage", "not_started"),
            "revenue_verified": bool(request.get("revenue_verified", False) or workflow_id in latest_verification),
            "age_hours": age_hours,
            "engagement_event": (latest_engagement.get(workflow_id) or {}).get("event"),
            "followup_status": _followup_status(latest_engagement.get(workflow_id), now_dt),
        }
        effective_request = dict(request)
        effective_request["revenue_verified"] = row["revenue_verified"]
        row["next_action"] = _next_action(effective_request, latest.get(workflow_id), latest_engagement.get(workflow_id))
        rows.append(row)
    return sorted(rows, key=lambda row: (row["revenue_verified"], -(row["age_hours"] or 0), row["workflow_id"]))
