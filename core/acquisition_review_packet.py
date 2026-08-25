def build_review_packet(prospect):
    return {
        "business_name": prospect.get("business_name"),
        "source": prospect.get("source"),
        "public_facts": {
            "abn": prospect.get("abn"),
            "location": prospect.get("location")
        },
        "verified_customer_intent": False,
        "outreach_ready": False,
        "human_decision_required": True
    }
