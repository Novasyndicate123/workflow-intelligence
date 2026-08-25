from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


class FunnelStore:
    """Small append-only funnel event store for commercial attribution."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, opportunity_id, stage, *, market="english_worldwide", geography="global"):
        event = {
            "opportunity_id": opportunity_id,
            "stage": stage,
            "market": market,
            "geography": geography,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self.path.open("a", encoding="utf-8-sig") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def _load(self):
        if not self.path.exists():
            return []
        events = []
        for line in self.path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events

    def events(self, opportunity_id=None):
        events = self._load()
        if opportunity_id is None:
            return events
        return [event for event in events if event["opportunity_id"] == opportunity_id]

    def summary(self):
        counts = {}
        for event in self._load():
            stage = event["stage"]
            counts[stage] = counts.get(stage, 0) + 1
        return counts
