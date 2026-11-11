import pytest
from pydantic import ValidationError

from drm.backend.scoring import rank_stages
from drm.schemas import *  # noqa: F403


def stage(i, deps=()):
    return Stage(id=i, name=f"s{i}", description="d", source_text=f"{i}. s{i}", depends_on=list(deps))


def analysis(sid, suit=4, effort=3, sev=3, rev=Reversibility.PARTIAL, hil=HumanInLoop.REVIEW_AFTER):
    return StageAnalysis(
        stage_id=sid,
        intervention=Intervention(primary=InterventionType.PERCEPTION, suitability=suit, rationale="r"),
        integration=Integration(data_required=["x"], interfaces=["y"], latency=LatencyClass.BATCH,
                                human_in_loop=hil, effort=effort, rationale="r"),
        risk=Risk(failure_modes=[FailureMode(description="f", severity=sev, reversibility=rev,
                                             detectable_before_harm=True)], regulatory_exposure=2),
        layer_placement=LayerPlacement.SLOW, confidence=Confidence.MEDIUM)


def test_valid_process():
    ProcessModel(process_name="p", stages=[stage(1), stage(2, deps=[1])])


def test_duplicate_ids_rejected():
    with pytest.raises(ValidationError):
        ProcessModel(process_name="p", stages=[stage(1), stage(1)])


def test_unknown_dependency_rejected():
    with pytest.raises(ValidationError):
        ProcessModel(process_name="p", stages=[stage(1, deps=[9])])


def test_severe_irreversible_needs_human_approval():
    with pytest.raises(ValidationError):
        analysis(1, sev=5, rev=Reversibility.IRREVERSIBLE, hil=HumanInLoop.NONE)
    analysis(1, sev=5, rev=Reversibility.IRREVERSIBLE, hil=HumanInLoop.APPROVE_BEFORE)


def test_extra_fields_rejected():
    with pytest.raises(ValidationError):
        Stage(id=1, name="a", description="d", source_text="1. a", surprise="x")


def test_ranking_prefers_safe_easy_fit():
    safe = analysis(1, suit=4, effort=2, sev=2, rev=Reversibility.REVERSIBLE)
    risky = analysis(2, suit=4, effort=2, sev=5, rev=Reversibility.IRREVERSIBLE,
                     hil=HumanInLoop.APPROVE_BEFORE)
    assert rank_stages([risky, safe])[0][0] == 1


