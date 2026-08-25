from core.acquisition_review_packet import build_review_packet


def test_review_packet_separates_public_facts_from_unverified_intent():
    prospect = {
        "business_name": "ACCOUNTANT MELBOURNE",
        "abn": "99668420732",
        "location": "3000 VIC",
        "qualification_score": 0.92,
        "source": "ABN_LOOKUP_PUBLIC",
        "public_source_only": True,
        "review_status": "READY_FOR_HUMAN_REVIEW",
        "external_send_authorized": False,
        "execution_authorized": False,
    }
    packet = build_review_packet(prospect)
    assert packet["business_name"] == "ACCOUNTANT MELBOURNE"
    assert packet["public_facts"]["abn"] == "99668420732"
    assert packet["public_facts"]["location"] == "3000 VIC"
    assert packet["verified_customer_intent"] is False
    assert packet["outreach_ready"] is False
    assert packet["human_decision_required"] is True
    assert packet["source"] == "ABN_LOOKUP_PUBLIC"
