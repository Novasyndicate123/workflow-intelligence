from core.prioritized_candidates import prioritize_with_verified_outcomes
from core.verified_economic_outcome import VerifiedEconomicOutcome


def _record():
    record = {
        "workflow_id": "wf-1", "record_id": "rec-1", "transaction_id": "tx-1",
        "outcome_id": "out-1", "status": "VERIFIED_ECONOMIC_OUTCOME",
        "verified_revenue_value": 1000.0, "currency": "AUD",
        "metrics": {"net_value": 900.0}, "learning_eligible": True, "immutable": True,
    }
    record["fingerprint"] = VerifiedEconomicOutcome._fingerprint(record)
    return record


def test_verified_outcome_strengthens_candidate_evidence_without_promoting_it():
    proposals = [{"id": "cand-1", "expected_upside": 0.6, "evidence_strength": 0.2,
                  "uncertainty": 0.2, "implementation_cost": 0.2, "risk": 0.1}]
    result = prioritize_with_verified_outcomes(proposals, {"cand-1": _record()})
    row = result["ranked"][0]
    assert row["evidence_strength"] == 0.9
    assert row["lineage"]["gate"] == "verified_economic_outcome"
    assert row["lineage"]["state"] == "candidate"


def test_unverified_outcome_cannot_change_candidate_ranking():
    proposals = [{"id": "cand-1", "expected_upside": 0.6, "evidence_strength": 0.2,
                  "uncertainty": 0.2, "implementation_cost": 0.2, "risk": 0.1}]
    record = _record()
    record["learning_eligible"] = False
    result = prioritize_with_verified_outcomes(proposals, {"cand-1": record})
    assert result["ranked"] == []
