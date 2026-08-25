import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from core.smb_response_evidence import is_placeholder_note


ACTIONS = {"REVIEWED", "REJECTED", "PROMOTE"}


class SMBResponseReviewQueue:
    """Append-only human review queue for SMB response evidence."""

    def __init__(self, path="results/smb_response_reviews.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _records(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    @staticmethod
    def _fingerprint(record: dict) -> str:
        body = {k: v for k, v in record.items() if k != "record_fingerprint"}
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def submit(self, response: dict) -> dict:
        if not response.get("response_id") or not response.get("fingerprint"):
            raise ValueError("source_response_required")
        if is_placeholder_note(response.get("note")):
            raise ValueError("placeholder_note_not_allowed")
        if any(r.get("response_id") == response["response_id"] for r in self._records()):
            raise ValueError("response_already_queued")
        item = {
            "review_id": uuid.uuid4().hex,
            "response_id": response["response_id"],
            "source_fingerprint": response["fingerprint"],
            "classification": response["classification"],
            "evidence_score": float(response.get("evidence_score", 0.0) or 0.0),
            "consent": bool(response.get("consent")),
            "status": "PENDING",
            "promoted": False,
            "reviewer_id": None,
            "reason": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        item["record_fingerprint"] = self._fingerprint(item)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(item, sort_keys=True) + "\n")
        return item

    def review(self, response_id: str, *, reviewer_id: str, action: str, reason: str) -> dict:
        action = str(action or "").upper()
        if action not in ACTIONS:
            raise ValueError("invalid_review_action")
        if not reviewer_id or not reason.strip():
            raise ValueError("reviewer_and_reason_required")
        previous = self._latest(response_id)
        if previous is None:
            raise ValueError("response_not_queued")
        if previous.get("status") != "PENDING":
            raise ValueError("already_reviewed")
        if action == "PROMOTE" and not previous.get("consent"):
            raise ValueError("consent_required")
        status = "PROMOTED" if action == "PROMOTE" else action
        updated = dict(previous)
        updated.update({
            "status": status,
            "promoted": action == "PROMOTE",
            "reviewer_id": reviewer_id,
            "reason": reason.strip(),
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        })
        updated["record_fingerprint"] = self._fingerprint(updated)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(updated, sort_keys=True) + "\n")
        return updated

    def _latest(self, response_id: str):
        current = None
        for record in self._records():
            if record.get("response_id") == response_id:
                current = record
        return current
