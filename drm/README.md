# Deployment Readiness Mapper (DRM)

The DRM takes a numbered description of an industrial or physical process and returns a structured analysis of where an AI agent could act, what connecting it would take, and what could go wrong. It is the first module of the Robothropic AI Physical AI Toolkit.

It is an analysis aid for a process engineer. It does not size benefits, validate a design, or replace the process owner's accountability.

## What it does

Three agents run in sequence. Each model reply is checked against a strict schema and retried on failure.

```
numbered process description
   -> Decomposer   stages, actors, systems, records, dependencies, rework paths, open questions
   -> Analyst      per stage: intervention, integration surface, risk profile (anchored 1-5 scales)
   -> Synthesizer  executive summary, priority map, cross-cutting risks, open questions
   -> report (JSON + Markdown)
```

Ranking, priority tiers, the limitations text and the provisional flag are computed in code, not written by a model. A complete report can be built offline from the scores with no model call.

**Provisional until approved.** A report is PROVISIONAL unless a named person has answered every open question of the process model (see "Approval" below).

## Run it

From the repository root, with the virtual environment active and `ANTHROPIC_API_KEY` set:

```
python -m drm.backend.pipeline drm/examples/optical_coating_line.md --oversight mandatory --out report_out
```

This writes four files into `report_out/`: the report (`.md` and `.json`), the process model (`.processmodel.json`) and the analysis (`.analysis.json`).

Options: `--oversight mandatory|recommended|unspecified` (a constraint supplied with the process, not decided by a model), `--narrative model|offline` (offline needs no third call), `--out FOLDER`, `--name BASE`, `--approval FILE`, `--open`.

The model and effort are set in `drm/backend/config.py` or with the environment variables `DRM_MODEL` and `DRM_EFFORT`.

Without API credit, `python -m drm.backend.bridge` runs each stage by hand through a chat window and applies the same checks. Results from that route approximate the live path; they are not identical to it.

## Approval

The questions come from the Decomposer, so approval is a second run:

1. Run the pipeline once. Read the open questions in the report.
2. Write an approval file: `{"approved_by": "Name", "resolutions": [{"question": "<exact question text>", "answer": "..."}]}`. Every question must be answered, or the run is refused.
3. Run again from the saved process model: `python -m drm.backend.pipeline report_out/NAME.processmodel.json --approval approval.json`.

## Examples (`drm/examples/`)

- `optical_coating_line.md`: an illustrative 10-stage anti-reflective coating line with human operators and no AI in it.
- `optical_coating_line.processmodel.json`: the reference process model. **Hand-authored**, not model output.
- `optical_coating_line.analysis.json` and `optical_coating_line_report.md/.json`: the Analyst scores come from a manual run through a chat window, with one stray empty field and one interface wording edited by hand (recorded in the report's provenance line). The wording of the report is generated from templates.
- `adhesive_batch_line.md` and `.processmodel.json`: a deliberately messy input with an instruction planted in stage 8. The process model is a genuine model reply, formatting only.

## Tests

```
python -m pytest drm/tests -q
```

The tests use stand-in clients: no key and no network. They cover the schemas, the checks on each agent's output, the scoring, the report, the glossary and the pipeline code.

## Status and limitations

State of the evidence:

- The one-command pipeline is tested with stand-in clients. **It has not yet been run against the live API.**
- The Decomposer produced valid output on both examples through a chat window. One sample per input; variance is not measured.
- The Analyst was run by hand on the optical line. A first attempt failed two engineering checks and was retried. A reviewer judged one rating too high. The prompt was changed afterwards and the full chain has not been re-run with it.
- The FastAPI layer and the frontend are not built.

Limits of the method:

- Scores are judgments made by a language model on anchored scales, applied to a description written by people. They are a starting point for review, not measurements.
- The priority formula (fit minus effort minus worst-case severity, with a penalty for irreversible failures) has uncalibrated weights. It has no benefit term, gives no credit for human oversight, and ignores the analyst's confidence. It ranks feasibility and risk, not value.
- The DRM scores where an AI agent could act. It does not assess whether a stage suits classical automation or a robotic system. "AI role: none" does not mean there is no automation opportunity.
- Accountability for the process, the safety envelope, quality obligations and the decision to deploy stays with the process owner.

Licence: Apache 2.0.

