import json
from pathlib import Path

import pytest

from core.smb_response_evidence import SMBResponseEvidenceStore
from core.smb_response_review import SMBResponseReviewQueue
from core.promoted_response_opportunity_bridge import PromotedResponseOpportunityBridge


def _stores(tmp_path):
    evidence = SMBResponseEvidenceStore(tmp_path / "responses.jsonl")
    queue = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    row = evidence.record(
        experiment_run_id="78fa7486907c4da8b851a8e01a729f58",
        classification="problem_confirmed",
        note="Manual workflow is recurring and costly.",
        consent=True,
        source_channel="human_interview",
    )
    queue.submit(row)
    queue.review(row["response_id"], reviewer_id="operator", action="PROMOTE", reason="Direct customer signal confirmed recurring pain.")
    return row, queue


def test_promoted_response_strengthens_opportunity_evidence(tmp_path):
    row, queue = _stores(tmp_path)
    bridge = PromotedResponseOpportunityBridge(queue)
    result = bridge.apply(
        opportunity={"id": "smb-workflow-audit", "evidence_confidence": 0.5},
        response_id=row["response_id"],
    )
    assert result["status"] == "PROMOTED_EVIDENCE_APPLIED"
    assert result["evidence_confidence"] > 0.5
    assert result["revenue_verified"] is False
    assert result["execution_authorized"] is False


def test_unpromoted_response_cannot_affect_opportunity(tmp_path):
    evidence = SMBResponseEvidenceStore(tmp_path / "responses.jsonl")
    queue = SMBResponseReviewQueue(tmp_path / "reviews.jsonl")
    row = evidence.record("run-1", "problem_confirmed", "possible problem", True, "human_interview")
    queue.submit(row)
    bridge = PromotedResponseOpportunityBridge(queue)
    with pytest.raises(ValueError, match="promoted_response_required"):
        bridge.apply({"id": "x", "evidence_confidence": 0.5}, row["response_id"])


def test_tampered_review_cannot_affect_opportunity(tmp_path):
    row, queue = _stores(tmp_path)
    path = Path(tmp_path / "reviews.jsonl")
    data = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    data[-1]["source_fingerprint"] = "tampered"
    path.write_text("\n".join(json.dumps(x, sort_keys=True) for x in data) + "\n")
    bridge = PromotedResponseOpportunityBridge(queue)
    with pytest.raises(ValueError, match="invalid_review_integrity"):
        bridge.apply({"id": "x", "evidence_confidence": 0.5}, row["response_id"])
