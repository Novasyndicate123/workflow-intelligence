from __future__ import annotations

from .verified_economic_outcome import VerifiedEconomicOutcome
from .ranking_lineage import attach_ranking_lineage


class VerifiedOutcomeLearning:
    """Convert verified economic truth into a bounded ranking-learning signal."""

    def derive(self, record: dict, *, candidate_id: str) -> dict:
        if record.get("status") != "VERIFIED_ECONOMIC_OUTCOME":
            raise ValueError("verified_economic_outcome_required")
        if record.get("learning_eligible") is not True:
            raise ValueError("verified_economic_outcome_required")
        if not VerifiedEconomicOutcome.verify_record(record):
            raise ValueError("invalid_economic_outcome_fingerprint")
        revenue = float(record.get("verified_revenue_value", 0.0) or 0.0)
        net_value = float((record.get("metrics") or {}).get("net_value", 0.0) or 0.0)
        if revenue <= 0.0 or net_value <= 0.0:
            raise ValueError("positive_economic_value_required")
        margin = net_value / revenue
        multiplier = max(0.1, min(1.0, margin))
        base = {
            "candidate_id": candidate_id,
            "verified_revenue_value": revenue,
            "net_value": net_value,
            "learning_multiplier": multiplier,
            "gate": "verified_economic_outcome",
            "evidence_ids": [str(record["record_id"])],
            "state": "candidate",
        }
        return attach_ranking_lineage(
            base,
            evidence_ids=base["evidence_ids"],
            state="candidate",
            learning_multiplier=multiplier,
            gate="verified_economic_outcome",
        )
