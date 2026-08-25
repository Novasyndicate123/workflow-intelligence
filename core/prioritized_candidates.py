from .experiment_prioritizer import prioritize_candidates
from .verified_outcome_learning import VerifiedOutcomeLearning


def prioritize_with_verified_outcomes(proposals, outcomes_by_candidate):
    enriched = []
    learner = VerifiedOutcomeLearning()
    for proposal in proposals:
        candidate_id = proposal.get("id", "")
        outcome = (outcomes_by_candidate or {}).get(candidate_id)
        row = dict(proposal)
        if outcome is not None:
            try:
                signal = learner.derive(outcome, candidate_id=candidate_id)
            except ValueError:
                continue
            row["evidence_strength"] = max(
                float(row.get("evidence_strength", 0.0) or 0.0),
                signal["learning_multiplier"],
            )
            row["lineage"] = signal["lineage"]
        enriched.append(row)
    return prioritize_experiment_proposals(enriched)


def prioritize_experiment_proposals(proposals):
    normalized = []
    for proposal in proposals:
        normalized.append({
            "id": proposal.get("id", ""),
            "upside": proposal.get("expected_upside"),
            "evidence": proposal.get("evidence_strength"),
            "evidence_strength": proposal.get("evidence_strength"),
            "uncertainty": proposal.get("uncertainty"),
            "cost": proposal.get("implementation_cost"),
            "risk": proposal.get("risk"),
            "execution_authorized": False,
            "lineage": proposal.get("lineage"),
        })
    return prioritize_candidates(normalized)
