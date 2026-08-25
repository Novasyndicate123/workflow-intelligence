import pytest

from core.verified_outcome_learning import VerifiedOutcomeLearning
from core.verified_economic_outcome import VerifiedEconomicOutcome


def verified_record():
    return {
        "workflow_id": "wf-1",
        "record_id": "rec-1",
        "transaction_id": "tx-1",
        "outcome_id": "out-1",
        "status": "VERIFIED_ECONOMIC_OUTCOME",
        "verified_revenue_value": 1500.0,
        "currency": "AUD",
        "metrics": {"net_value": 1200.0, "success_rate": 1.0},
        "learning_eligible": True,
        "immutable": True,
        "fingerprint": "placeholder",
    }


def test_rejects_unverified_record():
    record = verified_record()
    record["learning_eligible"] = False
    with pytest.raises(ValueError, match="verified_economic_outcome_required"):
        VerifiedOutcomeLearning().derive(record, candidate_id="cand-1")


def test_rejects_tampered_record():
    record = verified_record()
    with pytest.raises(ValueError, match="invalid_economic_outcome_fingerprint"):
        VerifiedOutcomeLearning().derive(record, candidate_id="cand-1")


def test_derives_bounded_learning_signal_from_verified_outcome():
    store = VerifiedEconomicOutcome()
    record = dict(verified_record())
    body = dict(record)
    body.pop("fingerprint")
    record["fingerprint"] = store._fingerprint(body)
    signal = VerifiedOutcomeLearning().derive(record, candidate_id="cand-1")
    assert 0.0 < signal["learning_multiplier"] <= 1.0
    assert signal["gate"] == "verified_economic_outcome"
    assert signal["evidence_ids"] == ["rec-1"]
    assert signal["candidate_id"] == "cand-1"
