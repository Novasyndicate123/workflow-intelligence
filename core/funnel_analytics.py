from __future__ import annotations


class FunnelAnalytics:
    STAGES = (
        "discovered",
        "qualified",
        "assessed",
        "engaged",
        "replied",
        "pilot_candidate",
        "converted",
    )
    COMMERCIAL_STAGES = (
        "assessed",
        "offer_viewed",
        "pilot_request_started",
        "pilot_candidate",
    )

    def analyze(self, events: list[dict]) -> dict:
        by_opportunity: dict[str, set[str]] = {}
        all_stages = tuple(dict.fromkeys(self.STAGES + self.COMMERCIAL_STAGES))
        counts = {stage: 0 for stage in all_stages}
        segments: dict[str, dict[str, int]] = {}
        for event in events:
            oid = str(event.get("opportunity_id", ""))
            stage = event.get("stage")
            if stage not in counts or not oid:
                continue
            by_opportunity.setdefault(oid, set()).add(stage)
            geography = event.get("geography", "global")
            segment = segments.setdefault(geography, {name: 0 for name in all_stages})
            segment[stage] += 1
        for seen in by_opportunity.values():
            for stage in seen:
                counts[stage] += 1
        def transition_rates(stages):
            rates = {}
            for left, right in zip(stages, stages[1:]):
                denominator = counts[left]
                rates[f"{left}_to_{right}"] = counts[right] / denominator if denominator else None
            return rates
        rates = transition_rates(self.STAGES)
        commercial_rates = transition_rates(self.COMMERCIAL_STAGES)
        bottleneck_key = None
        measured = [(key, value) for key, value in rates.items() if value is not None and value > 0.0]
        if measured:
            bottleneck_key = min(measured, key=lambda item: item[1])[0]
        commercial_bottleneck = None
        commercial_measured = [(key, value) for key, value in commercial_rates.items() if value is not None and value > 0.0]
        if commercial_measured:
            commercial_bottleneck = min(commercial_measured, key=lambda item: item[1])[0]
        return {"counts": counts, "transition_rates": rates, "commercial_transition_rates": commercial_rates, "bottleneck": bottleneck_key, "commercial_bottleneck": commercial_bottleneck, "segments": segments}
