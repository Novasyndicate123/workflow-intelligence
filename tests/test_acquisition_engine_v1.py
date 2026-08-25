import pytest
from core.acquisition_engine_v1 import AcquisitionEngineV1


def test_qualify_public_business_candidate():
    engine = AcquisitionEngineV1()
    result = engine.qualify({
        "business_id": "abn-123",
        "name": "Example Services",
        "status": "active",
        "location": "VIC",
        "workflow_signal": "manual enquiry triage",
    })
    assert result["status"] == "READY_FOR_REVIEW"
    assert result["business_id"] == "abn-123"
    assert result["public_source_only"] is True
    assert result["external_send_authorized"] is False
    assert result["execution_authorized"] is False


def test_reject_non_public_contact_fields():
    engine = AcquisitionEngineV1()
    with pytest.raises(ValueError, match="private_contact_data_not_allowed"):
        engine.qualify({
            "business_id": "abn-1",
            "name": "Example",
            "email": "owner@example.com",
        })


def test_build_outreach_draft_without_sending():
    engine = AcquisitionEngineV1()
    result = engine.build_outreach_draft({
        "business_id": "abn-2",
        "name": "Example Services",
        "workflow_signal": "manual enquiry triage",
    })
    assert result["status"] == "DRAFT_READY"
    assert result["external_send_authorized"] is False
    assert result["sent"] is False
