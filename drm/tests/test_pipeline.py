"""Pipeline tests. A fake client stands in for the API: no key, no network."""
import json
from pathlib import Path

import pytest

from drm.backend import pipeline
from drm.schemas import (ApprovedProcessModel, Constraints, HumanOversight, ProcessModel)
from drm.tests.test_analyst import FIXTURE, PROCESS, FakeClient, reply

SOURCE = Path(FIXTURE).with_name("optical_coating_line.md")
TEXT = SOURCE.read_text(encoding="utf-8")
MANDATORY = Constraints(human_oversight=HumanOversight.MANDATORY)


def decomposer_reply():
    return FIXTURE.read_text(encoding="utf-8")


def synth_reply(provisional=True):
    summary = "Provisional analysis." if provisional else "Final analysis."
    return json.dumps({"executive_summary": summary, "cross_cutting_risks": ["Records span stages 8 and 10."],
                       "stage_rationales": [{"stage_id": s.id, "rationale": f"Reason for stage {s.id}."}
                                            for s in PROCESS.stages]})


def approval():
    return {"approved_by": "N. Fernandes",
            "resolutions": [{"question": q, "answer": "settled"} for q in PROCESS.ambiguities]}


# ---------- run_pipeline ----------
def test_text_input_runs_all_three_agents_in_order():
    client = FakeClient([decomposer_reply(), reply(), synth_reply()])
    log = []
    result = pipeline.run_pipeline(TEXT, MANDATORY, client=client, log=log.append)
    assert len(client.calls) == 3
    assert result.report.provisional is True and result.report.narrative_source == "model"
    assert result.report.executive_summary == "Provisional analysis."
    assert [m.split(":")[0] for m in log if m.endswith("...")] == ["Decomposer", "Analyst", "Synthesizer"]
    assert "Produced by the DRM pipeline" in result.report.limitations and "no hand edits" in result.report.limitations
    assert "PROVISIONAL" in result.report.limitations and "classical automation" in result.report.limitations


def test_offline_narrative_makes_no_third_call():
    client = FakeClient([decomposer_reply(), reply()])
    result = pipeline.run_pipeline(TEXT, MANDATORY, narrative="offline", client=client)
    assert len(client.calls) == 2 and result.report.narrative_source == "offline"
    assert "Produced by the DRM pipeline" in result.report.limitations


def test_saved_process_model_skips_the_decomposer():
    client = FakeClient([reply()])
    result = pipeline.run_pipeline(PROCESS, narrative="offline", client=client)
    assert len(client.calls) == 1 and len(result.analysis.analyses) == 10


def test_approval_gives_a_final_report_and_wrong_approval_is_rejected():
    client = FakeClient([reply(), synth_reply(provisional=False)])
    result = pipeline.run_pipeline(PROCESS, approval=approval(), client=client)
    assert isinstance(result.process, ApprovedProcessModel)
    assert result.report.provisional is False and "PROVISIONAL" not in result.report.limitations
    with pytest.raises(ValueError):
        pipeline.run_pipeline(PROCESS, approval={"approved_by": "N. Fernandes", "resolutions": []},
                              client=FakeClient([]))
    with pytest.raises(ValueError):
        pipeline.run_pipeline(PROCESS, approval={**approval(), "approved_by": ""}, client=FakeClient([]))


def test_unknown_narrative_is_rejected():
    with pytest.raises(ValueError):
        pipeline.run_pipeline(PROCESS, narrative="other", client=FakeClient([]))


# ---------- command line ----------
def test_cli_writes_report_model_and_analysis_files(tmp_path, capsys):
    out = tmp_path / "out"
    client = FakeClient([decomposer_reply(), reply(), synth_reply()])
    code = pipeline.main(["pipeline", str(SOURCE), "--oversight", "mandatory", "--out", str(out),
                          "--name", "run1"], client=client)
    assert code == 0
    for suffix in (".md", ".json", ".processmodel.json", ".analysis.json"):
        assert (out / f"run1{suffix}").stat().st_size > 0
    assert json.loads((out / "run1.json").read_text(encoding="utf-8"))["provisional"] is True
    ProcessModel.model_validate_json((out / "run1.processmodel.json").read_text(encoding="utf-8"))
    md = (out / "run1.md").read_text(encoding="utf-8")
    assert "Status: PROVISIONAL" in md and "How to read the columns" in md
    text = capsys.readouterr().out
    assert "Decomposer: done" in text and "PROVISIONAL report" in text and str(out / "run1.md") in text


def test_cli_with_saved_model_and_approval_gives_a_final_report(tmp_path):
    approval_file = tmp_path / "approval.json"
    approval_file.write_text(json.dumps(approval()), encoding="utf-8")
    client = FakeClient([reply(), synth_reply(provisional=False)])
    code = pipeline.main(["pipeline", str(FIXTURE), "--approval", str(approval_file), "--out", str(tmp_path / "o"),
                          "--name", "final"], client=client)
    assert code == 0
    assert json.loads((tmp_path / "o" / "final.json").read_text(encoding="utf-8"))["provisional"] is False


def test_cli_stops_with_a_clear_message_when_replies_stay_invalid(tmp_path, capsys):
    client = FakeClient(["not json"] * 3)
    code = pipeline.main(["pipeline", str(SOURCE), "--out", str(tmp_path / "o")], client=client)
    assert code == 1
    assert "Pipeline stopped: DecompositionError" in capsys.readouterr().out
    assert not (tmp_path / "o").exists()


def test_cli_setup_problems_return_2(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert pipeline.main(["pipeline", str(SOURCE)]) == 2
    assert "ANTHROPIC_API_KEY is not set" in capsys.readouterr().out
    assert pipeline.main(["pipeline"], client=FakeClient([])) == 2
    assert pipeline.main(["pipeline", str(tmp_path / "missing.md")], client=FakeClient([])) == 2
    assert pipeline.main(["pipeline", str(SOURCE), "--oversight", "sometimes"], client=FakeClient([])) == 2
    assert pipeline.main(["pipeline", str(SOURCE), "--narrative", "other"], client=FakeClient([])) == 2

