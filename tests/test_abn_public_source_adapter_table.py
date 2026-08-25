from core.abn_public_source_adapter import ABNPublicSourceAdapter


def test_parse_table_results_captured_from_public_seed():
    html = """
    <table><tr><th>ABN</th><th>Name</th><th>Location</th></tr>
    <tr><td>84 535 887 044</td><td>MELBOURNE PLUMBING CO</td><td>3040 VIC</td></tr>
    </table>
    """
    results = ABNPublicSourceAdapter().parse_results(html, "Melbourne Plumbing")
    assert len(results) == 1
    assert results[0]["abn"] == "84535887044"
    assert results[0]["business_name"] == "MELBOURNE PLUMBING CO"
    assert results[0]["location"] == "3040 VIC"
    assert results[0]["source"] == "ABN_LOOKUP_PUBLIC"
    assert results[0]["public_source_only"] is True
