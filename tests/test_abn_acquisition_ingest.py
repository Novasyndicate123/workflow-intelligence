from core.abn_acquisition_ingest import ABNAcquisitionIngest

class StubAdapter:
    def __init__(self, rows):
        self.rows = rows

    def parse_results(self, html, query):
        return list(self.rows)

class StubEngine:
    def qualify_public_prospect(self, record):
        return {**record, "qualification_status": "READY_FOR_REVIEW"}

class StubBridge:
    def __init__(self):
        self.items = []

    def enqueue(self, prospect):
        self.items.append(prospect)
        return prospect

def test_ingest_deduplicates_abns_and_preserves_provenance():
    rows = [
        {"abn": "12345678901", "business_name": "A", "source": "ABN_LOOKUP_PUBLIC", "public_source_only": True, "query": "plumbing"},
        {"abn": "12345678901", "business_name": "A", "source": "ABN_LOOKUP_PUBLIC", "public_source_only": True, "query": "plumbing"},
    ]
    bridge = StubBridge()
    ingest = ABNAcquisitionIngest(StubAdapter(rows), StubEngine(), bridge)
    out = ingest.ingest("html", "plumbing")
    assert len(out) == 1
    assert len(bridge.items) == 1
    assert out[0]["source"] == "ABN_LOOKUP_PUBLIC"
    assert out[0]["public_source_only"] is True
    assert out[0]["external_send_authorized"] is False
    assert out[0]["execution_authorized"] is False
