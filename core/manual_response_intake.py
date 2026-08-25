from typing import Any, Optional


class ManualResponseIntake:
    """Local human-entry adapter for the SMB evidence ledger."""

    def __init__(self, evidence_store):
        self.evidence_store = evidence_store

    def record(
        self,
        experiment_run_id: str,
        classification: str,
        note: str,
        consent: bool,
        source_channel: str,
        response_id: Optional[str] = None,
    ) -> dict[str, Any]:
        if not str(experiment_run_id or "").strip():
            raise ValueError("experiment_run_id_required")
        row = self.evidence_store.record(
            experiment_run_id=experiment_run_id,
            classification=classification,
            note=note,
            consent=consent,
            source_channel=source_channel,
            response_id=response_id,
        )
        return {
            "status": "RECORDED",
            "response_id": row["response_id"],
            "evidence_score": row["evidence_score"],
            "fingerprint": row["fingerprint"],
            "promoted": False,
            "execution_authorized": False,
            "external_send_authorized": False,
        }
