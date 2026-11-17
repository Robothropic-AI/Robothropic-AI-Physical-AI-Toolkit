"""Synthesizer, renderer and report-command tests. No API, no network."""
import json
import os
from pathlib import Path

import pytest

from drm.backend import bridge, config, synthesizer as syn
from drm.backend.render import render_markdown
from drm.schemas import (AnalystOutput, ApprovedProcessModel, Constraints, HumanOversight,
                         ProcessModel, Resolution)

FIXTURE = Path(__file__).parents[1] / "examples" / "optical_coating_line.processmodel.json"
PROCESS = ProcessModel.model_validate_json(FIXTURE.read_text(encoding="utf-8"))

# stage_id: (suitability, effort, severity, primary)
PLAN = {1: (5, 1, 1, "perception"), 2: (4, 2, 2, "reasoning"), 3: (4, 2, 2, "perception"),
        4: (3, 3, 3, "reasoning"), 5: (3, 3, 3, "perception"), 6: (2, 4, 4, "perception"),
        7: (1, 1, 3, "none"), 8: (3, 3, 3, "reasoning"), 9: (2, 4, 4, "perception"),
        10: (2, 4, 4, "reasoning")}


def entry(stage_id, suit, effort, sev, primary):
    return {"stage_id": stage_id,
            "intervention": {"primary": primary, "secondary": [], "suitability": suit, "rationale": "reason"},
            "integration": {"data_required": ["d"], "interfaces": ["i"], "latency": "batch",
                            "human_in_loop": "review_after", "effort": effort, "rationale": "r"},
            "risk": {"failure_modes": [{"description": "f", "severity": sev, "reversibility": "partial",
                                        "detectable_before_harm": True}],
                     "regulatory_exposure": 3 if stage_id in (4, 8) else 2, "regulatory_note": ""},
            "layer_placement": "human_only" if primary == "none" else "slow",
            "confidence": "low" if stage_id in (6, 10) else "medium", "assumptions": []}


ANALYSIS = AnalystOutput.model_validate({"analyses": [entry(i, *PLAN[i]) for i in PLAN]})


def approved():
    return ApprovedProcessModel(process=PROCESS, approved_by="N. Fernandes",
                                resolutions=[Resolution(question=q, answer="settled") for q in PROCESS.ambiguities])


# ---------- tiers ----------
def test_tiers_ties_share_the_conservative_tier_and_none_is_tier_three():
    t = syn.tiers(ANALYSIS.analyses)
    assert {i for i, v in t.items() if v == 1} == {1, 2, 3}
    assert {i for i, v in t.items() if v == 2} == {4, 5, 8}
    assert {i for i, v in t.items() if v == 3} == {6, 7, 9, 10}


def test_limitations_are_always_present_and_flag_provisional_and_oversight():
    text = syn.standard_limitations(Constraints(human_oversight=HumanOversight.MANDATORY, notes=["no night shifts"]), True)
    for phrase in ("not calibrated", "no benefit term", "PROVISIONAL", "oversight constraint applied: mandatory", "no night shifts"):
        assert phrase in text
    assert "PROVISIONAL" not in syn.standard_limitations(Constraints(), False)


# ---------- offline report ----------
def test_offline_report_is_complete_and_deterministic():
    r = syn.build_report(PROCESS, ANALYSIS, Constraints(human_oversight=HumanOversight.MANDATORY))
    assert r.narrative_source == "offline" and r.provisional is True
    assert [p.stage_id for p in r.priorities][0] == 1 and len(r.priorities) == 10
    assert r.open_questions_for_partner == PROCESS.ambiguities
    assert "provisional" in r.executive_summary.lower() and r.limitations
    assert r == syn.build_report(PROCESS, ANALYSIS, Constraints(human_oversight=HumanOversight.MANDATORY))


def test_approved_model_gives_a_final_report_without_open_questions():
    r = syn.build_report(approved(), ANALYSIS)
    assert r.provisional is False and r.open_questions_for_partner == [] and len(r.resolutions) == len(PROCESS.ambiguities)
    assert "provisional" not in r.executive_summary.lower()


# ---------- model wording checks ----------
def test_synthesis_checks():
    good = syn.offline_narrative(PROCESS, ANALYSIS, True)
    syn.check_synthesis(good, ANALYSIS, True)
    missing = good.model_copy(update={"stage_rationales": good.stage_rationales[:-1]})
    with pytest.raises(ValueError, match="cover stages"):
        syn.check_synthesis(missing, ANALYSIS, True)
    with pytest.raises(ValueError, match="provisional"):
        syn.check_synthesis(good.model_copy(update={"executive_summary": "All good."}), ANALYSIS, True)
    with pytest.raises(ValueError, match="words"):
        syn.check_synthesis(good.model_copy(update={"executive_summary": "provisional " * 300}), ANALYSIS, True)


def test_extra_keys_rejected_in_model_output():
    raw = json.loads(syn.offline_narrative(PROCESS, ANALYSIS, True).model_dump_json())
    raw["surprise"] = ""
    with pytest.raises(ValueError):
        syn.parse_and_check_synthesis(json.dumps(raw), ANALYSIS, True)


def test_prompts_carry_the_facts_and_rules():
    s = syn.build_synth_system_prompt()
    assert "Never add keys of your own" in s and "JSON Schema" in s
    u = syn.build_synth_user_prompt(PROCESS, ANALYSIS, Constraints(human_oversight=HumanOversight.MANDATORY))
    assert "<status>PROVISIONAL</status>" in u and '"tier": 1' in u and "<open_questions>" in u
    assert "<status>FINAL</status>" in syn.build_synth_user_prompt(approved(), ANALYSIS)


class _Block:
    type = "text"

    def __init__(self, text):
        self.text = text


class _Resp:
    def __init__(self, text):
        self.content = [_Block(text)]


class FakeClient:
    def __init__(self, outputs):
        self.outputs, self.calls = list(outputs), []
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        return _Resp(self.outputs.pop(0))


def test_synthesize_live_path_with_retry():
    good = syn.offline_narrative(PROCESS, ANALYSIS, True).model_dump_json()
    client = FakeClient(["not json", good])
    r = syn.synthesize(PROCESS, ANALYSIS, client=client)
    assert r.narrative_source == "model" and len(client.calls) == 2
    assert client.calls[0]["model"] == config.MODEL and client.calls[0]["output_config"] == {"effort": config.EFFORT}
    with pytest.raises(syn.SynthesisError):
        syn.synthesize(PROCESS, ANALYSIS, client=FakeClient(["x", "y"]), max_retries=1)


# ---------- markdown ----------
def test_markdown_structure_and_pipe_escaping():
    narrative = syn.offline_narrative(PROCESS, ANALYSIS, True)
    narrative.stage_rationales[0] = narrative.stage_rationales[0].model_copy(update={"rationale": "left | right"})
    md = render_markdown(syn.build_report(PROCESS, ANALYSIS, narrative=narrative))
    for heading in ("# Deployment Readiness Report", "## Executive summary", "## Priority map", "## Stage details",
                    "## Cross-cutting risks", "## Open questions for the partner", "## Limitations", "PROVISIONAL"):
        assert heading in md
    assert "left / right" in md and "left | right" not in md
    assert sum(1 for line in md.splitlines() if line[:3] in ("| 1", "| 2", "| 3")) == 10


def test_final_markdown_lists_resolutions():
    md = render_markdown(syn.build_report(approved(), ANALYSIS))
    assert "FINAL" in md and "### Resolved questions" in md and "settled" in md


# ---------- bridge commands ----------
def test_bridge_report_commands(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    Path("analysis.json").write_text(ANALYSIS.model_dump_json(), encoding="utf-8")
    assert bridge.main(["bridge", "report", str(FIXTURE), "analysis.json", "--oversight", "mandatory"]) == 0
    assert "PROVISIONAL" in Path("drm_report.md").read_text(encoding="utf-8")
    DRM = json.loads(Path("drm_report.json").read_text(encoding="utf-8"))
    assert DRM["narrative_source"] == "offline"

    assert bridge.main(["bridge", "report-prompt", str(FIXTURE), "analysis.json"]) == 0
    assert "<status>PROVISIONAL</status>" in Path("bridge_report_prompt.txt").read_text(encoding="utf-8")

    good = syn.offline_narrative(PROCESS, ANALYSIS, True).model_dump_json()
    monkeypatch.setattr(bridge, "read_clipboard", lambda: good)
    assert bridge.main(["bridge", "report-check", str(FIXTURE), "analysis.json", "--clipboard"]) == 0
    assert json.loads(Path("drm_report.json").read_text(encoding="utf-8"))["narrative_source"] == "model"

    monkeypatch.setattr(bridge, "read_clipboard", lambda: "Sorry, no JSON here")
    assert bridge.main(["bridge", "report-check", str(FIXTURE), "analysis.json", "--clipboard"]) == 1
    assert "INVALID" in capsys.readouterr().out and os.path.exists("bridge_report_retry_prompt.txt")


def test_report_command_rejects_an_analysis_that_breaks_the_constraint(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    data = json.loads(ANALYSIS.model_dump_json())
    data["analyses"][0]["integration"]["human_in_loop"] = "none"
    Path("analysis.json").write_text(json.dumps(data), encoding="utf-8")
    assert bridge.main(["bridge", "report", str(FIXTURE), "analysis.json", "--oversight", "mandatory"]) == 1
    assert "mandatory" in capsys.readouterr().out and not os.path.exists("drm_report.md")


