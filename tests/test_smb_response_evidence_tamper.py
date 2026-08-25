import json
import pytest
from core.smb_response_evidence import SMBResponseEvidenceStore


def test_fingerprint_detects_tampering(tmp_path):
    path = tmp_path / "responses.jsonl"
    store = SMBResponseEvidenceStore(path)
    row = store.record("run-1", "pilot_interest", "Please evaluate the pilot", True, "business_community")
    payload = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    payload["note"] = "altered"
    assert payload["fingerprint"] != store._fingerprint(payload)
