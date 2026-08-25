from __future__ import annotations


class AcquisitionReviewIntegration:
    """Bridge approved acquisition handoffs into human-reviewed response capture."""

    def __init__(self, evidence_store, review_queue):
        self.evidence_store = evidence_store
        self.review_queue = review_queue

    def prepare_response_capture(self, handoff: dict, *, experiment_run_id: str) -> dict:
        if handoff.get("status") != "READY_FOR_HUMAN_REVIEW":
            raise ValueError("handoff_not_ready_for_human_review")
        opportunity_id = str(handoff.get("opportunity_id", "")).strip()
        run_id = str(experiment_run_id or "").strip()
        if not opportunity_id:
            raise ValueError("opportunity_id_required")
        if not run_id:
            raise ValueError("experiment_run_id_required")
        return {
            "status": "READY_FOR_RESPONSE_CAPTURE",
            "opportunity_id": opportunity_id,
            "experiment_run_id": run_id,
            "source": handoff.get("source", ""),
            "context": handoff.get("context", ""),
            "human_review_required": True,
            "external_send_authorized": False,
            "execution_authorized": False,
            "evidence_promotion_authorized": False,
        }

    def record_and_queue(
        self,
        *,
        experiment_run_id: str,
        classification: str,
        note: str,
        consent: bool,
        source_channel: str,
    ) -> dict:
        response = self.evidence_store.record(
            experiment_run_id=experiment_run_id,
            classification=classification,
            note=note,
            consent=consent,
            source_channel=source_channel,
        )
        review = self.review_queue.submit(response)
        return {
            "status": "QUEUED_FOR_HUMAN_REVIEW",
            "response_id": response["response_id"],
            "review_id": review["review_id"],
            "promoted": False,
            "execution_authorized": False,
            "external_send_authorized": False,
        }
