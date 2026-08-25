from core.abn_public_source_adapter import ABNPublicSourceAdapter

SAMPLE_HTML = '''
<table>
<tr><th>ABN</th><th>Name</th><th>Type</th><th>Location</th></tr>
<tr><td>12 345 678 901</td><td>EXAMPLE PLUMBING PTY LTD</td><td>Entity Name</td><td>3000 VIC</td></tr>
<tr><td>98 765 432 109</td><td>EXAMPLE CAFE</td><td>Business Name</td><td>4000 QLD</td></tr>
</table>
'''


def test_parse_public_results_only():
    adapter = ABNPublicSourceAdapter()
    results = adapter.parse_results(SAMPLE_HTML, query="plumbing")
    assert len(results) == 2
    assert results[0]["abn"] == "12345678901"
    assert results[0]["business_name"] == "EXAMPLE PLUMBING PTY LTD"
    assert results[0]["source"] == "ABN_LOOKUP_PUBLIC"
    assert results[0]["public_source_only"] is True


def test_never_collects_private_contact_fields():
    html = SAMPLE_HTML.replace("<td>4000 QLD</td>", "<td>4000 QLD</td><td>owner@example.com</td>")
    adapter = ABNPublicSourceAdapter()
    result = adapter.parse_results(html, query="cafe")[0]
    assert "email" not in result
    assert "phone" not in result
    assert "contact" not in result


def test_service_mode_requires_explicit_guid():
    adapter = ABNPublicSourceAdapter()
    assert adapter.service_enabled is False
    assert adapter.service_guid is None
