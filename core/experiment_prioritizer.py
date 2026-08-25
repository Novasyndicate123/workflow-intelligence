WEIGHTS = {
    "upside": 0.30,
    "evidence": 0.25,
    "uncertainty": -0.15,
    "cost": -0.15,
    "risk": -0.15,
}


def _information_efficiency(candidate):
    gain = float(candidate.get("expected_information_gain", 0.0) or 0.0)
    cost = max(1.0, float(candidate.get("cost", 0.0) or 0.0))
    return gain / cost


def prioritize_candidates(candidates):
    ranked = []
    excluded = []
    for candidate in candidates:
        fields = [candidate.get(key) for key in WEIGHTS]
        if any(value is None for value in fields):
            excluded.append(candidate.get("id", ""))
            continue
        priority = sum(float(candidate[key]) * weight for key, weight in WEIGHTS.items())
        ranked.append({
            **candidate,
            "priority": round(priority, 4),
            "information_efficiency": round(_information_efficiency(candidate), 6),
        })
    ranked.sort(key=lambda row: (-row["priority"], -row["information_efficiency"], str(row.get("id", ""))))
    return {"ranked": ranked, "excluded": excluded}
