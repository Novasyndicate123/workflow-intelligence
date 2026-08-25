from __future__ import annotations

from dataclasses import dataclass


STAGES = (
    "signal", "pain", "intent", "opportunity", "solution", "pilot",
    "proof", "offer", "transaction", "fulfillment", "outcome", "decision",
)


@dataclass(frozen=True)
class LineageLink:
    source_stage: str
    source_id: str
    target_stage: str
    target_id: str
    evidence_status: str


class EconomicLineage:
    def __init__(self):
        self._links: dict[tuple[str, str], LineageLink] = {}

    def add_link(self, link: LineageLink) -> LineageLink:
        self._validate(link)
        key = (link.source_stage, link.source_id)
        existing = self._links.get(key)
        if existing and (existing.target_stage != link.target_stage or existing.target_id != link.target_id):
            raise ValueError("conflicting_lineage_link")
        if existing and existing.evidence_status != link.evidence_status:
            raise ValueError("conflicting_evidence_status")
        self._links[key] = link
        return link

    def trace_from(self, stage: str, entity_id: str) -> dict:
        self._validate_stage(stage)
        if not entity_id:
            raise ValueError("entity_id_required")
        if stage == STAGES[-1]:
            return {"status": "complete", "terminal_stage": stage, "terminal_id": entity_id, "links": []}
        index = STAGES.index(stage)
        current_stage, current_id = stage, entity_id
        links = []
        while index < len(STAGES) - 1:
            link = self._links.get((current_stage, current_id))
            if link is None:
                return {"status": "unresolved", "missing_stage": STAGES[index + 1], "links": links}
            if link.evidence_status != "verified":
                return {"status": "unresolved", "reason": "unverified_link", "links": links + [link]}
            expected_target = STAGES[index + 1]
            if link.target_stage != expected_target:
                return {"status": "unresolved", "reason": "lineage_gap", "missing_stage": expected_target, "links": links + [link]}
            links.append(link)
            current_stage, current_id = link.target_stage, link.target_id
            index += 1
        return {"status": "complete", "terminal_stage": current_stage, "terminal_id": current_id, "links": links}

    @property
    def links(self) -> tuple[LineageLink, ...]:
        return tuple(self._links.values())

    @staticmethod
    def _validate_stage(stage: str):
        if stage not in STAGES:
            raise ValueError("unsupported_lineage_stage")

    @classmethod
    def _validate(cls, link: LineageLink):
        cls._validate_stage(link.source_stage)
        cls._validate_stage(link.target_stage)
        if STAGES.index(link.target_stage) <= STAGES.index(link.source_stage):
            raise ValueError("invalid_stage_transition")
        if not link.source_id or not link.target_id:
            raise ValueError("lineage_id_required")
        if link.evidence_status not in {"verified", "unverified"}:
            raise ValueError("invalid_evidence_status")
