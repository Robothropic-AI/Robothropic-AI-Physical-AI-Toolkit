"""Decomposer tests. A fake client stands in for the API: no key, no network."""
import json
from pathlib import Path

import pytest

from drm.backend import config
from drm.backend.decomposer import (DecompositionError, build_system_prompt,
                                    decompose, numbered_lines)

EXAMPLE = (Path(__file__).parents[1] / "examples" / "optical_coating_line.md").read_text(encoding="utf-8")


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

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _Resp(self.outputs.pop(0))


def good_payload(drop=None, alter=None):
    stages = []
    for i, line in numbered_lines(EXAMPLE).items():
        if i == drop:
            continue
        stages.append({"id": i, "name": f"stage {i}", "description": line,
                       "source_text": "changed" if i == alter else line,
                       "depends_on": [i - 1] if i > 1 else [],
                       "rework_to": [2] if i == 10 else []})
    return {"process_name": "AR coating line", "stages": stages}


def good(**kw):
    return json.dumps(good_payload(**kw))


def test_example_has_ten_numbered_lines():
    assert sorted(numbered_lines(EXAMPLE)) == list(range(1, 11))


def test_success_and_request_shape():
    client = FakeClient([good()])
    model = decompose(EXAMPLE, client=client)
    assert len(model.stages) == 10
    assert model.stages[9].rework_to == [2]
    call = client.calls[0]
    assert call["model"] == config.MODEL
    assert call["output_config"] == {"effort": config.EFFORT}
    assert "temperature" not in call and "tool_choice" not in call


def test_code_fences_are_stripped():
    assert len(decompose(EXAMPLE, client=FakeClient(["```json\n" + good() + "\n```"])).stages) == 10


def test_retry_after_invalid_json():
    client = FakeClient(["this is not json", good()])
    decompose(EXAMPLE, client=client)
    assert len(client.calls) == 2
    assert "validation_error" in client.calls[1]["messages"][0]["content"]


def test_retry_after_dropped_stage():
    client = FakeClient([good(drop=5), good()])
    decompose(EXAMPLE, client=client)
    assert len(client.calls) == 2


def test_altered_source_text_rejected_then_fixed():
    client = FakeClient([good(alter=3), good()])
    decompose(EXAMPLE, client=client)
    assert len(client.calls) == 2


def test_gives_up_after_retry_budget():
    client = FakeClient(["nope", "nope"])
    with pytest.raises(DecompositionError):
        decompose(EXAMPLE, client=client, max_retries=1)
    assert len(client.calls) == 2


def test_prompt_embeds_schema_and_rules():
    p = build_system_prompt()
    assert "rework_to" in p and "ONLY one JSON object" in p

