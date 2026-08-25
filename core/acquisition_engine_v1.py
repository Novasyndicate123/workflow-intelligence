from __future__ import annotations


class AcquisitionEngineV1:
    """Public-data prospect qualifier and non-sending outreach drafter."""

    _PRIVATE_CONTACT_FIELDS = {
        "email", "phone", "mobile", "contact_email", "contact_phone",
        "owner_email", "owner_phone", "personal_email", "personal_phone",
    }

    def qualify(self, candidate: dict) -> dict:
        if self._private_fields(candidate):
            raise ValueError("private_contact_data_not_allowed")
        business_id = str(candidate.get("business_id", "")).strip()
        name = str(candidate.get("name", "")).strip()
        status = str(candidate.get("status", "")).strip().lower()
        signal = str(candidate.get("workflow_signal", "")).strip()
        if not business_id:
            raise ValueError("business_id_required")
        if not name:
            raise ValueError("business_name_required")
        if status != "active":
            raise ValueError("inactive_business_not_eligible")
        if not signal:
            raise ValueError("workflow_signal_required")
        return {
            "status": "READY_FOR_REVIEW",
            "business_id": business_id,
            "business_name": name,
            "location": candidate.get("location", ""),
            "workflow_signal": signal,
            "public_source_only": True,
            "external_send_authorized": False,
            "execution_authorized": False,
        }

    def build_outreach_draft(self, candidate: dict) -> dict:
        if self._private_fields(candidate):
            raise ValueError("private_contact_data_not_allowed")
        name = str(candidate.get("name", "")).strip()
        signal = str(candidate.get("workflow_signal", "")).strip()
        if not name or not signal:
            raise ValueError("draft_context_required")
        return {
            "status": "DRAFT_READY",
            "business_id": str(candidate.get("business_id", "")).strip(),
            "subject": "A quick workflow question",
            "body": f"Hi {name}, we noticed a possible workflow opportunity around {signal}. "
            "Would you be open to a brief conversation about how you currently handle it?",
            "sent": False,
            "external_send_authorized": False,
        }

    @classmethod
    def _private_fields(cls, candidate: dict) -> set[str]:
        return {key for key in cls._PRIVATE_CONTACT_FIELDS if key in candidate and candidate.get(key)}
