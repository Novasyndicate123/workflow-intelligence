from __future__ import annotations


class CommercialExperimentSelector:
    """Select the strongest existing zero-budget commercial test without authorizing execution."""

    def select(self, wedges, commercial_validation):
        if not commercial_validation or not commercial_validation.get("candidates"):
            raise ValueError("commercial_validation_required")
        validation = {str(row.get("segment", "")).lower(): row for row in commercial_validation["candidates"]}
        eligible = []
        for wedge in wedges or []:
            if float(wedge.get("budget_limit", 0.0) or 0.0) != 0.0:
                continue
            row = validation.get(str(wedge.get("customer_type", "")).lower())
            if not row or row.get("validation") != "TEST":
                continue
            eligible.append((int(row.get("rank", 999)), float(row.get("score", 0.0)), wedge, row))
        if not eligible:
            if any(float(w.get("budget_limit", 0.0) or 0.0) != 0.0 for w in (wedges or [])):
                raise ValueError("zero_budget_required")
            raise ValueError("no_test_candidate_available")
        _, _, wedge, evidence = sorted(eligible, key=lambda item: (item[0], -item[1]))[0]
        return {
            "status": "DRAFT",
            "candidate": dict(wedge),
            "evidence": dict(evidence),
            "decision": commercial_validation.get("decision", ""),
            "rationale": evidence.get("reason", "existing commercial validation"),
            "success_metrics": list(wedge.get("success_metrics", [])),
            "kill_criteria": list(wedge.get("kill_criteria", [])),
            "budget_limit": 0.0,
            "approval_required": True,
            "external_send_authorized": False,
            "execution_authorized": False,
        }
