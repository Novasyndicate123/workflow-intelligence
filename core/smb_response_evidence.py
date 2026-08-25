from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

CLASSIFICATIONS = {
    "problem_confirmed",
    "offer_requested",
    "pilot_interest",
    "not_interested",
    "unclear",
}

PLACEHOLDER_NOTES = {
    "ACTUAL CUSTOMER RESPONSE HERE",
    "PASTE THE ACTUAL CUSTOMER RESPONSE HERE",
}


def is_placeholder_note(note: str) -> bool:
    normalized = " ".join(str(note or "").strip().upper().split())
    if normalized in PLACEHOLDER_NOTES:
        return True
    if "CUSTOMER RESPONSE" in normalized and (" HERE" in normalized or normalized.startswith("PASTE ")):
        return True
    if normalized.startswith("EXACT CUSTOMER WORDS") and normalized.endswith("HERE"):
        return True
    return False


class SMBResponseEvidenceStore:
    """Append-only ledger for human-entered SMB validation responses."""

    def __init__(self, path="results/smb_response_evidence.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _records(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    @staticmethod
    def _fingerprint(row):
        body = {k: v for k, v in row.items() if k != "fingerprint"}
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def record(self, experiment_run_id, classification, note, consent, source_channel, response_id=None):
        classification = str(classification or "").strip()
        note = str(note or "").strip()
        source_channel = str(source_channel or "").strip()
        if classification not in CLASSIFICATIONS:
            raise ValueError("invalid_classification")
        if not note:
            raise ValueError("note_required")
        if is_placeholder_note(note):
            raise ValueError("placeholder_note_not_allowed")
        if not source_channel:
            raise ValueError("source_channel_required")
        response_id = str(response_id or uuid.uuid4().hex)
        if any(r.get("response_id") == response_id for r in self._records()):
            raise ValueError("duplicate_response_id")
        timestamp = datetime.now(timezone.utc).isoformat()
        row = {
            "response_id": response_id,
            "experiment_run_id": str(experiment_run_id),
            "classification": classification,
            "note": note,
            "consent": bool(consent),
            "source_channel": source_channel,
            "timestamp": timestamp,
            "evidence_score": self._score(classification, consent),
        }
        row["fingerprint"] = self._fingerprint(row)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    @staticmethod
    def _score(classification, consent):
        base = {
            "problem_confirmed": 0.60,
            "offer_requested": 0.80,
            "pilot_interest": 1.00,
            "not_interested": 0.10,
            "unclear": 0.20,
        }[classification]
        return round(base if consent else base * 0.5, 3)

    def records(self):
        return self._records()
