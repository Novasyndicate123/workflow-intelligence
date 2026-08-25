import pytest

from core.acquisition_review_queue_bridge import AcquisitionReviewQueueBridge


class FakeQueue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)
        return item["review_id"]


def test_bridge_enqueues_qualified_public_prospect_for_review():
    queue = FakeQueue()
    bridge = AcquisitionReviewQueueBridge(queue)
    prospect = {
        "business_name": "Example Pty Ltd",
        "abn": "12345678901",
        "location": "VIC 3000",
        "qualification_score": 0.82,
        "source": "ABN_LOOKUP_PUBLIC",
        "outreach_draft": "Draft only",
    }
    result = bridge.enqueue_prospect(prospect)
    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["review_id"] == queue.items[0]["review_id"]
    assert result["external_send_authorized"] is False
    assert result["execution_authorized"] is False
