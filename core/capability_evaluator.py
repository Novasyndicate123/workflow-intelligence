from __future__ import annotations

class CapabilityEvaluator:
    def compare(self, prediction, outcome):
        expected=prediction.get('expected',{})
        observed=outcome.get('observed',{})
        matches=all(observed.get(k)==v for k,v in expected.items())
        return {'prediction_error':'hit' if matches else 'miss','validated':bool(outcome.get('validated',False)),'expected':expected,'observed':observed}
    def score(self, history):
        total=len(history)
        hits=sum(1 for item in history if item.get('prediction_error')=='hit')
        rate=hits/total if total else 0.0
        return {'capability_score':round(rate,6),'sample_size':total}
