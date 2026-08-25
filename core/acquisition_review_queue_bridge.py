import uuid


class AcquisitionReviewQueueBridge:
    def __init__(self, queue):
        self.queue = queue

    def enqueue_prospect(self, prospect):
        # Validate business_name/source
        if not prospect.get('business_name') or not prospect.get('source'):
            raise ValueError("business_name and source are required")

        # Create UUID review_id
        review_id = str(uuid.uuid4())

        # Create item with required fields
        item = {
            'review_id': review_id,
            'status': 'READY_FOR_HUMAN_REVIEW',
            'business_name': prospect['business_name'],
            'abn': prospect.get('abn'),
            'location': prospect.get('location'),
            'qualification_score': prospect.get('qualification_score'),
            'source': prospect['source'],
            'outreach_draft': prospect.get('outreach_draft'),
            'external_send_authorized': False,
            'execution_authorized': False,
            'sent': False,
        }
        # Enqueue item
        self.queue.enqueue(item)

        return item
