"""Deterministic ranking. Plain code, not an LLM judgment: same input, same ranking.

The weights are a starting point, not calibrated. Calibrating them against
real processes is future work and should be stated openly in the article.
"""
from drm.schemas import Reversibility, StageAnalysis

W_EFFORT = 0.5
W_SEVERITY = 0.5
IRREVERSIBLE_PENALTY = 1.0


def priority_score(a: StageAnalysis) -> float:
    """Higher = better first candidate: strong fit, low effort, low worst-case risk."""
    worst_severity = max(f.severity for f in a.risk.failure_modes)
    irreversible = any(f.reversibility == Reversibility.IRREVERSIBLE
                       for f in a.risk.failure_modes)
    return (a.intervention.suitability
            - W_EFFORT * a.integration.effort
            - W_SEVERITY * worst_severity
            - (IRREVERSIBLE_PENALTY if irreversible else 0.0))


def rank_stages(analyses: list[StageAnalysis]) -> list[tuple[int, float]]:
    """Return (stage_id, score) best-first; ties broken by stage_id for stability."""
    scored = [(a.stage_id, priority_score(a)) for a in analyses]
    return sorted(scored, key=lambda t: (-t[1], t[0]))
