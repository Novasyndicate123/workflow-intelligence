from __future__ import annotations

_FUTURE_FIELDS = {
    "success", "revenue", "outcome", "outcome_verified",
    "realized_revenue", "actual_value",
}
_ALLOWED_STATES = {"candidate", "promoted", "frozen", "recovering"}


def attach_ranking_lineage(row, *, evidence_ids, state, learning_multiplier, gate):
    if not evidence_ids:
        raise ValueError("evidence_ids must not be empty")
    if state not in _ALLOWED_STATES:
        raise ValueError("invalid adaptive state")
    multiplier = float(learning_multiplier)
    if not 0.0 <= multiplier <= 1.0:
        raise ValueError("learning_multiplier must be in [0, 1]")
    candidate_id = row.get("candidate_id", row.get("id"))
    if not candidate_id:
        raise ValueError("candidate_id is required")
    lineage = {
        "candidate_id": candidate_id,
        "evidence_ids": list(evidence_ids),
        "state": state,
        "learning_multiplier": multiplier,
        "gate": str(gate),
    }
    return {**row, "lineage": lineage}
