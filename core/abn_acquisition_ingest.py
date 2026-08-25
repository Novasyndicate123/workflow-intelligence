class ABNAcquisitionIngest:
    def __init__(self, adapter, engine, bridge):
        self.adapter = adapter
        self.engine = engine
        self.bridge = bridge

    def ingest(self, html, query):
        results = self.adapter.parse_results(html, query)
        seen_abns = set()
        enqueued_prospects = []

        for record in results:
            abn = record.get('abn')
            if not abn:
                continue

            normalized_abn = abn.replace(' ', '')
            if normalized_abn in seen_abns:
                continue

            seen_abns.add(normalized_abn)
            record['abn'] = normalized_abn
            record['source'] = record.get('source', '')
            record['public_source_only'] = record.get('public_source_only', False)
            record['query'] = query

            qualified_record = self.engine.qualify_public_prospect(record)
            qualified_record['external_send_authorized'] = False
            qualified_record['execution_authorized'] = False

            prospect = self.bridge.enqueue(qualified_record)
            enqueued_prospects.append(prospect)

        return enqueued_prospects