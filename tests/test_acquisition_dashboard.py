from core.acquisition_dashboard import render_dashboard


def test_acquisition_dashboard_renders_aggregates_only():
    report = {
        "counts": {"discovered": 10, "qualified": 4, "assessed": 2},
        "transition_rates": {"discovered_to_qualified": 0.4, "qualified_to_assessed": 0.5},
        "bottleneck": "discovered_to_qualified",
        "segments": {"south_asia": {"discovered": 6, "qualified": 2}},
    }
    html = render_dashboard(report)
    assert "10" in html
    assert "40.0%" in html
    assert "discovered_to_qualified" in html
    assert "south_asia" in html
    assert "customer enquiry" not in html.lower()
    assert "participant_id" not in html.lower()
    assert "payment_value" not in html.lower()


def test_acquisition_dashboard_renders_ranked_review_batch_without_send_authority():
    report = {
        "counts": {"discovered": 11, "qualified": 11, "assessed": 0},
        "transition_rates": {"discovered_to_qualified": 1.0},
        "bottleneck": "qualified_to_assessed",
        "segments": {"global": {"discovered": 11, "qualified": 11}},
    }
    batch = [{
        "business_name": "ACCOUNTANT MELBOURNE", "abn": "99668420732",
        "location": "3000 VIC", "qualification_score": 0.92,
        "source": "ABN_LOOKUP_PUBLIC", "public_source_only": True,
        "review_status": "READY_FOR_HUMAN_REVIEW",
        "external_send_authorized": False, "execution_authorized": False,
    }]
    html = render_dashboard(report, review_batch=batch)
    assert "ACCOUNTANT MELBOURNE" in html
    assert "3000 VIC" in html
    assert "92.0%" in html
    assert "READY_FOR_HUMAN_REVIEW" in html
    assert "ABN_LOOKUP_PUBLIC" in html
    assert "external_send_authorized" not in html.lower()
    assert "execution_authorized" not in html.lower()
