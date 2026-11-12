import json
from pathlib import Path

from drm.backend.bridge import check_reply, make_prompt, summarise
from drm.backend.decomposer import numbered_lines

EXAMPLE = (Path(__file__).parents[1] / "examples" / "optical_coating_line.md").read_text(encoding="utf-8")


def reply(drop=None):
    stages = [{"id": i, "name": f"stage {i}", "description": t, "source_text": t,
               "depends_on": [i - 1] if i > 1 else [], "rework_to": [2] if i == 10 else []}
              for i, t in numbered_lines(EXAMPLE).items() if i != drop]
    return json.dumps({"process_name": "AR coating line", "stages": stages})


def test_prompt_contains_rules_schema_and_input():
    p = make_prompt(EXAMPLE)
    assert "JSON Schema" in p and "rework_to" in p and "Incoming inspection" in p


def test_valid_reply_with_chat_prose_and_fence():
    chatty = "Here is the model:\n```json\n" + reply() + "\n```\nLet me know if you want changes."
    model, err = check_reply(EXAMPLE, chatty)
    assert model is not None and err == "" and len(model.stages) == 10
    assert "VALID" not in summarise(model) and "rework_to=[2]" in summarise(model)


def test_dropped_stage_is_reported():
    model, err = check_reply(EXAMPLE, reply(drop=10))
    assert model is None and "do not match" in err


def test_non_json_is_reported():
    model, err = check_reply(EXAMPLE, "Sorry, I cannot do that.")
    assert model is None and err


