from core.acquisition_review_batch import AcquisitionReviewBatch


def test_ranked_review_batch_preserves_governance():
    prospects = [
        {
            "abn": "12345678901",
            "business_name": "BETA",
            "location": "3000 VIC",
            "source": "ABN_LOOKUP_PUBLIC",
            "public_source_only": True,
            "qualification_status": "READY_FOR_REVIEW",
            "qualification_score": 0.7,
        },
        {
            "abn": "10987654321",
            "business_name": "ALPHA",
            "location": "3040 VIC",
            "source": "ABN_LOOKUP_PUBLIC",
            "public_source_only": True,
            "qualification_status": "READY_FOR_REVIEW",
            "qualification_score": 0.9,
        },
    ]
    batch = AcquisitionReviewBatch().build(prospects)
    assert [p["business_name"] for p in batch] == ["ALPHA", "BETA"]
    assert all(p["review_status"] == "READY_FOR_HUMAN_REVIEW" for p in batch)
    assert all(p["external_send_authorized"] is False for p in batch)
    assert all(p["execution_authorized"] is False for p in batch)
    assert all(p["public_source_only"] is True for p in batch)
