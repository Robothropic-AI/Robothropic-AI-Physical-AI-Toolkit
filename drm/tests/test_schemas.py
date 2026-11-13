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


def _s(i, deps=(), rework=()):
    return Stage(id=i, name=f"s{i}", description="d", source_text=f"{i}. s{i}",
                 depends_on=list(deps),
                 rework_to=[ReworkEdge(to=t, when="test condition") for t in rework])


def test_rework_loop_allowed():
    ProcessModel(process_name="p", stages=[_s(1), _s(2, deps=[1]), _s(3, deps=[2], rework=[1])])


def test_rework_to_unknown_stage_rejected():
    with pytest.raises(ValidationError):
        ProcessModel(process_name="p", stages=[_s(1), _s(2, deps=[1], rework=[9])])


def test_rework_forward_rejected():
    with pytest.raises(ValidationError):
        ProcessModel(process_name="p", stages=[_s(1, rework=[2]), _s(2, deps=[1])])


def test_cycle_in_depends_on_rejected():
    with pytest.raises(ValidationError):
        ProcessModel(process_name="p", stages=[_s(1, deps=[2]), _s(2, deps=[1])])


def test_self_dependency_rejected():
    with pytest.raises(ValidationError):
        ProcessModel(process_name="p", stages=[_s(1, deps=[1])])


def test_rework_edge_requires_a_condition():
    with pytest.raises(ValidationError):
        ReworkEdge(to=2, when="")
    with pytest.raises(ValidationError):
        ReworkEdge(to=2)


def test_systems_and_records_default_empty_and_accept_values():
    s = Stage(id=1, name="a", description="d", source_text="1. a", systems=["PLC"], records=["Batch record"])
    assert s.systems == ["PLC"] and s.records == ["Batch record"] and s.actors == []


@pytest.mark.parametrize("field", ["actors", "systems", "records"])
def test_hedged_names_rejected(field):
    with pytest.raises(ValidationError):
        Stage(id=1, name="a", description="d", source_text="1. a", **{field: ["QC personnel (implied)"]})


def _pm(ambiguities):
    return ProcessModel(process_name="p", stages=[stage(1)], ambiguities=ambiguities)


def test_approval_requires_every_ambiguity_resolved():
    pm = _pm(["Who confirms base pressure?", "Where are witness samples loaded?"])
    with pytest.raises(ValidationError):
        ApprovedProcessModel(process=pm, approved_by="N. Fernandes",
                             resolutions=[Resolution(question="Who confirms base pressure?", answer="Process engineer")])
    ok = ApprovedProcessModel(process=pm, approved_by="N. Fernandes", resolutions=[
        Resolution(question="Who confirms base pressure?", answer="Process engineer"),
        Resolution(question="Where are witness samples loaded?", answer="In the dome, stage 3")])
    assert ok.approved_by == "N. Fernandes"


def test_approval_rejects_unknown_question_and_missing_approver():
    pm = _pm(["Q1?"])
    with pytest.raises(ValidationError):
        ApprovedProcessModel(process=pm, approved_by="x", resolutions=[
            Resolution(question="Q1?", answer="a"), Resolution(question="Typo?", answer="b")])
    with pytest.raises(ValidationError):
        ApprovedProcessModel(process=pm, approved_by="", resolutions=[Resolution(question="Q1?", answer="a")])


def test_model_with_no_ambiguities_can_be_approved():
    ApprovedProcessModel(process=_pm([]), approved_by="N. Fernandes")

