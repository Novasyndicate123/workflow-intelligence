import pytest

from core.economic_lineage import EconomicLineage, LineageLink
from core.verified_economic_outcome import VerifiedEconomicOutcome


def _lineage():
    graph = EconomicLineage()
    ids = ["sig-1", "pain-1", "intent-1", "opp-1", "sol-1", "pilot-1",
           "proof-1", "offer-1", "tx-1", "ful-1", "out-1", "decision-1"]
    stages = ["signal", "pain", "intent", "opportunity", "solution", "pilot",
              "proof", "offer", "transaction", "fulfillment", "outcome", "decision"]
    for source_stage, source_id, target_stage, target_id in zip(
        stages, ids, stages[1:], ids[1:]
    ):
        graph.add_link(LineageLink(source_stage, source_id, target_stage, target_id, "verified"))
    return graph


def test_records_verified_economic_outcome_with_complete_lineage(tmp_path):
    record = VerifiedEconomicOutcome(tmp_path / "outcomes.jsonl").record(
        workflow_id="wf-1",
        transaction={"transaction_id": "tx-1", "status": "paid", "payment_status": "paid", "sale_confirmed": True},
        fulfillment={"workflow_id": "wf-1", "stage": "outcome_recorded", "outcome_id": "out-1"},
        revenue={"workflow_id": "wf-1", "verified_revenue_value": 1500, "currency": "AUD", "evidence_reference": "invoice-1"},
        metrics={"net_value": 1200, "success_rate": 1.0},
        lineage=_lineage(),
        origin_stage="signal",
        origin_id="sig-1",
    )
    assert record["status"] == "VERIFIED_ECONOMIC_OUTCOME"
    assert record["learning_eligible"] is True
    assert record["verified_revenue_value"] == 1500.0
    assert record["lineage"]["status"] == "complete"
    assert record["outcome_id"] == "out-1"


def test_rejects_unpaid_or_unverified_economic_outcome(tmp_path):
    store = VerifiedEconomicOutcome(tmp_path / "outcomes.jsonl")
    with pytest.raises(ValueError, match="verified_payment_required"):
        store.record(
            workflow_id="wf-1",
            transaction={"transaction_id": "tx-1", "status": "pending", "payment_status": "pending", "sale_confirmed": False},
            fulfillment={"workflow_id": "wf-1", "stage": "outcome_recorded", "outcome_id": "out-1"},
            revenue={"workflow_id": "wf-1", "verified_revenue_value": 1500, "currency": "AUD", "evidence_reference": "invoice-1"},
            metrics={"net_value": 1200}, lineage=_lineage(), origin_stage="signal", origin_id="sig-1",
        )


def test_rejects_incomplete_lineage_without_learning_eligibility(tmp_path):
    graph = EconomicLineage()
    graph.add_link(LineageLink("signal", "sig-1", "pain", "pain-1", "verified"))
    store = VerifiedEconomicOutcome(tmp_path / "outcomes.jsonl")
    with pytest.raises(ValueError, match="complete_lineage_required"):
        store.record(
            workflow_id="wf-1",
            transaction={"transaction_id": "tx-1", "status": "paid", "payment_status": "paid", "sale_confirmed": True},
            fulfillment={"workflow_id": "wf-1", "stage": "outcome_recorded", "outcome_id": "out-1"},
            revenue={"workflow_id": "wf-1", "verified_revenue_value": 1500, "currency": "AUD", "evidence_reference": "invoice-1"},
            metrics={"net_value": 1200}, lineage=graph, origin_stage="signal", origin_id="sig-1",
        )


def test_rejects_duplicate_verified_outcome_for_workflow(tmp_path):
    path = tmp_path / "outcomes.jsonl"
    store = VerifiedEconomicOutcome(path)
    kwargs = dict(
        workflow_id="wf-1",
        transaction={"transaction_id": "tx-1", "status": "paid", "payment_status": "paid", "sale_confirmed": True},
        fulfillment={"workflow_id": "wf-1", "stage": "outcome_recorded", "outcome_id": "out-1"},
        revenue={"workflow_id": "wf-1", "verified_revenue_value": 1500, "currency": "AUD", "evidence_reference": "invoice-1"},
        metrics={"net_value": 1200}, lineage=_lineage(), origin_stage="signal", origin_id="sig-1",
    )
    store.record(**kwargs)
    with pytest.raises(ValueError, match="economic_outcome_already_verified"):
        store.record(**kwargs)


def test_reverifies_persisted_fingerprint(tmp_path):
    path = tmp_path / "outcomes.jsonl"
    store = VerifiedEconomicOutcome(path)
    record = store.record(
        workflow_id="wf-1",
        transaction={"transaction_id": "tx-1", "status": "paid", "payment_status": "paid", "sale_confirmed": True},
        fulfillment={"workflow_id": "wf-1", "stage": "outcome_recorded", "outcome_id": "out-1"},
        revenue={"workflow_id": "wf-1", "verified_revenue_value": 1500, "currency": "AUD", "evidence_reference": "invoice-1"},
        metrics={"net_value": 1200}, lineage=_lineage(), origin_stage="signal", origin_id="sig-1",
    )
    assert VerifiedEconomicOutcome(path).verify_record(record) is True


def test_persists_immutable_evidence_record(tmp_path):
    path = tmp_path / "outcomes.jsonl"
    store = VerifiedEconomicOutcome(path)
    record = store.record(
        workflow_id="wf-1",
        transaction={"transaction_id": "tx-1", "status": "paid", "payment_status": "paid", "sale_confirmed": True},
        fulfillment={"workflow_id": "wf-1", "stage": "outcome_recorded", "outcome_id": "out-1"},
        revenue={"workflow_id": "wf-1", "verified_revenue_value": 1500, "currency": "AUD", "evidence_reference": "invoice-1"},
        metrics={"net_value": 1200}, lineage=_lineage(), origin_stage="signal", origin_id="sig-1",
    )
    rows = VerifiedEconomicOutcome(path).records()
    assert rows[0]["record_id"] == record["record_id"]
    assert rows[0]["immutable"] is True
    assert rows[0]["evidence_reference"] == "invoice-1"
