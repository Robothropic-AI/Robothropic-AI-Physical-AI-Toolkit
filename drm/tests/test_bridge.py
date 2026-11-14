import json
from pathlib import Path

from drm.backend.bridge import check_reply, make_prompt, summarise
from drm.backend.decomposer import numbered_lines

EXAMPLE = (Path(__file__).parents[1] / "examples" / "optical_coating_line.md").read_text(encoding="utf-8")


def reply(drop=None):
    stages = [{"id": i, "name": f"stage {i}", "description": t, "source_text": t,
               "depends_on": [i - 1] if i > 1 else [], "rework_to": [{"to": 2, "when": "lot fails QC and is reworked"}] if i == 10 else []}
              for i, t in numbered_lines(EXAMPLE).items() if i != drop]
    return json.dumps({"process_name": "AR coating line", "stages": stages})


def test_prompt_contains_rules_schema_and_input():
    p = make_prompt(EXAMPLE)
    assert "JSON Schema" in p and "rework_to" in p and "Incoming inspection" in p


def test_valid_reply_with_chat_prose_and_fence():
    chatty = "Here is the model:\n```json\n" + reply() + "\n```\nLet me know if you want changes."
    model, err = check_reply(EXAMPLE, chatty)
    assert model is not None and err == "" and len(model.stages) == 10
    assert "VALID" not in summarise(model) and "->2 if lot fails QC and is reworked" in summarise(model)


def test_dropped_stage_is_reported():
    model, err = check_reply(EXAMPLE, reply(drop=10))
    assert model is None and "do not match" in err


def test_non_json_is_reported():
    model, err = check_reply(EXAMPLE, "Sorry, I cannot do that.")
    assert model is None and err


def test_reference_model_matches_the_example_and_is_not_approvable_yet():
    from drm.schemas import ApprovedProcessModel
    import pytest
    from pydantic import ValidationError
    fixture = (Path(__file__).parents[1] / "examples" / "optical_coating_line.processmodel.json").read_text(encoding="utf-8")
    model, err = check_reply(EXAMPLE, fixture)
    assert model is not None, err
    # open ambiguities exist, so the approval gate must refuse it
    with pytest.raises(ValidationError):
        ApprovedProcessModel(process=model, approved_by="someone")


def test_describe_shows_what_was_read():
    from drm.backend.bridge import describe
    text = "Get-Clipboard | Set-Content bridge_reply.json -Encoding utf8"
    d = describe(text)
    assert f"Read {len(text)} characters" in d and "Get-Clipboard" in d


def test_read_clipboard_uses_powershell(monkeypatch):
    import subprocess
    from drm.backend import bridge

    class Done:
        returncode, stdout, stderr = 0, "reply text", ""

    seen = {}

    def fake_run(cmd, **kw):
        seen["cmd"] = cmd
        return Done()

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert bridge.read_clipboard() == "reply text"
    assert seen["cmd"][0] == "powershell" and "Get-Clipboard" in seen["cmd"][-1]


def test_read_clipboard_failure_is_reported(monkeypatch):
    import subprocess
    import pytest
    from drm.backend import bridge

    class Bad:
        returncode, stdout, stderr = 1, "", "boom"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Bad())
    with pytest.raises(RuntimeError):
        bridge.read_clipboard()


def test_main_check_clipboard_flow(monkeypatch, tmp_path, capsys):
    import os
    from drm.backend import bridge
    proc = tmp_path / "p.md"
    proc.write_text(EXAMPLE, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(bridge, "read_clipboard", lambda: reply())
    assert bridge.main(["bridge", "check", str(proc), "--clipboard"]) == 0
    out = capsys.readouterr().out
    assert "Read " in out and "VALID" in out
    monkeypatch.setattr(bridge, "read_clipboard", lambda: "just a command line")
    assert bridge.main(["bridge", "check", str(proc), "--clipboard"]) == 1
    assert "just a command line" in capsys.readouterr().out and os.path.exists("bridge_retry_prompt.txt")


def test_adhesive_reference_reply_is_valid_for_its_input():
    base = Path(__file__).parents[1] / "examples"
    text = (base / "adhesive_batch_line.md").read_text(encoding="utf-8")
    reply_text = (base / "adhesive_batch_line.processmodel.json").read_text(encoding="utf-8")
    model, err = check_reply(text, reply_text)
    assert model is not None, err
    assert len(model.stages) == 9 and model.stages[4].rework_to[0].to == 4


