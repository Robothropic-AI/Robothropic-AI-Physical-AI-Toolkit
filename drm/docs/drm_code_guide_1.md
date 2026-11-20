# DRM Code Guide 1 of 6: The map

*Reading time about 15 minutes. Written for a technically literate reader who does not write Python daily.*

## The idea in four sentences

The DRM turns a numbered description of a process into a structured report. Three agents do it in sequence: one extracts structure, one scores it, one assembles and words the report. A language model does the judgment. Plain code does everything that has to be repeatable or checkable. Every model reply is validated against strict rules before anything else touches it.

## The journey of one process

```
numbered process description (.md or .txt)
        |
        v
  DECOMPOSER    decomposer.py     the model reads the text and returns a ProcessModel (JSON)
        |         checks: schema rules; each stage's source_text matches an input line
        v
  [ human approval, optional ]    approval.py     a named person answers the open questions
        |
        v
  ANALYST       analyst.py        the model scores every stage on three axes (JSON)
        |         checks: every stage covered; oversight rule; engineering consistency
        v
  SYNTHESIZER   synthesizer.py    code computes tiers, ranking and limitations;
        |                         a model (or plain templates) words the text
        v
  render.py + glossary.py         Markdown report and JSON report
```

The three axes the Analyst scores for each stage:

1. **Intervention**: where could an AI agent act (perception, reasoning, execution, communication, or none)?
2. **Integration**: what would connecting it take (data, interfaces, latency, human check, effort)?
3. **Risk**: what could go wrong (failure modes with severity, reversibility, regulatory exposure)?

## Who does what: model or code

| A model does | Code does |
|---|---|
| Reads the description and extracts stages, actors, systems, records | Validates every reply against the schemas |
| Judges the 1-5 scores on defined scales | Checks that each stage's source text is really in the input |
| Words the summary, the per-stage reasons and the cross-cutting risks (optional) | Ranks and tiers the stages with a fixed formula |
| | Writes the limitations text and sets the PROVISIONAL flag |
| | Enforces the human-oversight rules |
| | Builds the report files and defines abbreviations |

The design rule: **if a result must be the same every time, or must be checkable, code produces it**. The model supplies judgment, and its output is accepted only after the checks pass. If a check fails, the model is asked again with the error message, up to two retries (three attempts in total).

## The files

| File | Role | Guide |
|---|---|---|
| `drm/schemas/` | The data shapes and the rules about them | 2 |
| `drm/backend/decomposer.py` | Agent 1: description to process model | 3 |
| `drm/backend/analyst.py` | Agent 2: scores per stage | 3 |
| `drm/backend/scoring.py` | The ranking formula | 4 |
| `drm/backend/synthesizer.py` | Tiers, limitations, report assembly, optional model wording | 4 |
| `drm/backend/render.py` | Turns the report into Markdown | 5 |
| `drm/backend/glossary.py` | Defines abbreviations found in the report | 5 |
| `drm/backend/pipeline.py` | One command that runs the three agents | 5 |
| `drm/backend/bridge.py` | Manual route when no API credit is available | 5 |
| `drm/backend/config.py` | Model name and effort setting | 5 |
| `drm/tests/` | What each module promises, as runnable checks | 6 |
| `drm/examples/` | Worked inputs and outputs | any time |

**On the examples:** the optical coating process model is hand-authored. Its Analyst scores come from a manual run through a chat window, with two small hand edits recorded in the report's provenance line. The adhesive process model is a genuine model reply, formatting only.

## Four terms worth knowing

- **Validation**: a reply is converted into typed objects. Wrong types, missing fields, unknown fields or broken rules raise an error.
- **PROVISIONAL**: the process model has not been approved by a named person, so the open questions are still open. Every report is provisional unless an approval was supplied.
- **Offline**: the report wording comes from templates, with no model call. The scores themselves still came from the Analyst.
- **Stand-in client**: in the tests, a fake object replaces the API, so the tests need no key and no network.

## Experiment: build a report with no model at all

From the repository root, with the virtual environment active, on one line:

```
python -m drm.backend.bridge report drm/examples/optical_coating_line.processmodel.json drm/examples/optical_coating_line.analysis.json --oversight mandatory --out C:\Users\Utilizador\report_out --name map_test
```

This runs the last stage of the chain with no model call. The last printed line should read `Status: PROVISIONAL; tier 1: [1, 4]`. The files will be about 20 KB (`.md`) and 35 KB (`.json`).

Open `map_test.md` and find, in this order: the status line, the executive summary, the priority map with its legend, the stage details, the open questions, the limitations, the glossary. For each part, ask whether it came from the scores (model judgment) or from code.

## Check yourself

1. Which parts of an offline report involve a model? *(Only the scores, which the Analyst produced earlier. No wording is model-written.)*
2. Why does a report say PROVISIONAL? *(No named person has approved the process model, so its open questions remain open.)*
3. What happens when a model reply contains a field the schema does not define? *(It is rejected, and the model is asked again with the error message.)*
