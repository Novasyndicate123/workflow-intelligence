from __future__ import annotations

from .capability_registry import CapabilityRegistry


class QwenCapabilityPromotion:
    """Promote only verified Qwen execution evidence into capability routing."""

    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def promote(self, model, task_class, evidence_id, score, verified=False):
        if not verified:
            raise ValueError("UNVERIFIED_EVIDENCE")
        name = str(model)
        capability = str(task_class)
        existing = self.registry.get(name)
        if existing is None:
            return self.registry.register(
                name=name,
                capability=capability,
                version="30b" if "30b" in name else "local",
                evidence_ids=[str(evidence_id)],
                benchmark_scores={capability: float(score)},
            )
        if existing.get("capability") != capability:
            raise ValueError("CAPABILITY_MISMATCH")
        return self.registry.record_benchmark(
            name,
            capability,
            score,
            evidence_id,
            verified=True,
        )
