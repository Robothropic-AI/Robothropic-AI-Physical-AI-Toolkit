# DRM Code Guide 2 of 6: The schemas

*Folder: `drm/schemas/`. Reading time about 25 minutes. Read Guide 1 first.*

## What this folder is

The schemas define the **shape of every piece of data** that moves through the DRM, and the **rules that data must obey**. They use a library called Pydantic. Think of each schema as a specification sheet with acceptance tests: a model's reply is "incoming material", and the schema is the inspection at the dock. Material that fails does not enter the process; the sender is told why and asked to resupply.

Everything else in the DRM is written against these shapes, so this is the most useful folder to understand first.

`__init__.py` only re-exports the classes, which is why other files can write `from drm.schemas import StageAnalysis`.

## Reading order

| File | What it defines | Output of |
|---|---|---|
| `common.py` | Shared building blocks: the scale and the fixed vocabularies | |
| `process.py` | `Stage`, `ReworkEdge`, `ProcessModel` | Decomposer |
| `analysis.py` | `StageAnalysis` and its parts, `AnalystOutput` | Analyst |
| `approval.py` | `Resolution`, `ApprovedProcessModel` | A human |
| `constraints.py` | `HumanOversight`, `Constraints` | Supplied with the process |
| `report.py` | `PriorityEntry`, `DRMReport` | Synthesizer |

## `common.py`: the shared vocabulary

- **`Strict`** is the base class for every schema. It sets `extra="forbid"`: any field that is not defined is rejected. This catches invented or stray keys, which is the kind of problem that appeared in the manual Analyst run (a stray empty field).
- **`Scale`** is an integer from 1 to 5. The code does not use percentages, because a model cannot honestly justify "73% suitable". What each level means is defined in the Analyst prompt (the anchors in `analyst.py`), not here.
- **Enumerations** (fixed lists of allowed words): `InterventionType`, `LatencyClass`, `HumanInLoop`, `Reversibility`, `Confidence` and `LayerPlacement`. A value outside its list is an error.

**Watch for this:** `human_only` appears in two lists, with different questions behind it.
- In `HumanInLoop` it answers *who checks?* The stage is carried out by a person alone. The other values (`none`, `review_after`, `approve_before`) describe how a person checks an AI action.
- In `LayerPlacement` it answers *where does the AI action sit?* There is none. The other two values, `fast` and `slow`, tie each stage to the fast/slow layer thesis.

## `process.py`: what the Decomposer produces

A **`Stage`** holds the id, name, description, and these lists: `actors` (people and roles), `systems` (equipment and software), `records` (documents, logs, data systems), `inputs`, `outputs`, `depends_on` (stage ids), `rework_to` (loop-backs), and `source_text`, the exact input line that the stage comes from. That last field is what makes every later claim traceable.

A **`ReworkEdge`** is a loop-back: the stage it returns to (`to`) and the condition that triggers it (`when`).

A **`ProcessModel`** holds the process name, a list of stages, `assumptions` (what had to be inferred) and `ambiguities` (questions for the partner).

Its checks run when the object is created:
- Stage names in `actors`, `systems` and `records` may not contain hedge words (implied, assumed, likely, probably). Inferences belong in `assumptions` or `ambiguities`.
- Stage ids are unique, and `depends_on` and `rework_to` point only to stages that exist.
- A stage may not depend on itself, and `rework_to` may only point to the same stage or an earlier one.
- **`depends_on` must contain no cycles.** A function called `_require_acyclic` walks the graph one stage at a time. While it is exploring a stage's dependencies it marks that stage "visiting". Reaching a stage marked "visiting" means the walk has gone in a circle, and that is an error. Finished stages are marked "done" and skipped. It is the same logic as tracing a signal path and flagging an unintended feedback loop. Loops that are real must be declared with `rework_to`, with their trigger condition.

## `analysis.py`: what the Analyst produces

For each stage, a **`StageAnalysis`** holds three axes and a few extra fields:

- **`Intervention`**: `primary` (and `secondary`) type, `suitability` (1 to 5), rationale.
- **`Integration`**: `data_required`, `interfaces`, `latency`, `human_in_loop`, `effort` (1 to 5), rationale.
- **`Risk`**: a list of **`FailureMode`** items (description, severity 1 to 5, reversibility, whether it is detectable before harm), plus `regulatory_exposure` (1 to 5) and an optional note. A stage must have at least one failure mode.
- Also: `layer_placement`, `confidence`, and `assumptions`.

A `StageAnalysis` enforces two engineering rules:
1. A failure with severity 4 or 5 that is irreversible requires `human_in_loop` to be `approve_before` or `human_only`.
2. An AI role of `none` cannot come with a suitability above 2.

**`AnalystOutput`** is the whole reply: a list of `StageAnalysis` items, with no duplicate `stage_id`.

## `approval.py` and `constraints.py`

- **`Resolution`** is one question and its answer. The question must match an open ambiguity of the process model exactly.
- **`ApprovedProcessModel`** wraps a process model, the resolutions and an `approved_by` name that cannot be empty ("a named human, never the model"). It refuses to be created if any ambiguity is unanswered or any answered question was never raised.
- **`Constraints`** carries `human_oversight` (`mandatory`, `recommended` or `unspecified`) and free-text `notes`. It is supplied with the process, not produced by a model. Section 2 of the project addendum records why.

## `report.py`: what the Synthesizer assembles

- **`PriorityEntry`**: stage id, tier (1 to 3, 1 means start here) and a rationale. The tier is computed in code.
- **`DRMReport`**: the process, the analyses, the `provisional` flag, the oversight constraint, resolutions, the executive summary, priorities, cross-cutting risks, open questions, the limitations text (never empty) and `narrative_source` (`offline` or `model`). It checks that the priorities cover exactly the stages that were analysed.

## Rules enforced in code: the full list

| # | Rule | Where | Why |
|---|---|---|---|
| 1 | Unknown fields are rejected | `common.Strict` | Catches invented or stray keys |
| 2 | Scores are integers from 1 to 5 | `common.Scale` | No false precision |
| 3 | No hedge words inside actors, systems, records | `process.Stage` | Inferences go to assumptions |
| 4 | Stage ids are unique | `process.ProcessModel` | Unambiguous references |
| 5 | `depends_on` and `rework_to` point to real stages; no self-dependency | `process.ProcessModel` | A broken graph is useless |
| 6 | `rework_to` points to the same or an earlier stage | `process.ProcessModel` | Loops go backwards by definition |
| 7 | `depends_on` has no cycles | `process._require_acyclic` | Loops must be declared, with a trigger |
| 8 | At least one failure mode per stage | `analysis.Risk` | No stage is "risk-free" by omission |
| 9 | Severe and irreversible needs a human before action | `analysis.StageAnalysis` | Engineering consistency |
| 10 | AI role `none` cannot be a strong fit | `analysis.StageAnalysis` | No contradiction |
| 11 | No duplicate stage ids in the analyses | `analysis.AnalystOutput` | One entry per stage |
| 12 | Approval needs every question answered, none invented, and a named approver | `approval.ApprovedProcessModel` | The human gate |
| 13 | Priorities cover exactly the analysed stages; limitations never empty | `report.DRMReport` | A complete report |

**Where the other checks live:** some checks need two objects at once, so they are outside the schemas. That every stage of the process is covered, and the mandatory-oversight rule, are in `analyst.check_analysis` (Guide 3). That each stage's source text matches the input is in `decomposer.check_traceability` (Guide 3).

## Experiments

From the repository root, with the virtual environment active, type `python` to open the Python prompt. Paste one line at a time. A failed line prints a long block of red text; read the lines that follow `ValidationError`. Type `exit()` to leave.

**A. A hedge word in a name.**
```
from drm.schemas import Stage, ProcessModel
Stage(id=1, name="x", description="y", source_text="z", actors=["probably the operator"])
```
Expected: an error that says the name "hedges inside a name".

**B. An unknown field.**
```
Stage(id=1, name="x", description="y", source_text="z", colour="red")
```
Expected: `Extra inputs are not permitted`.

**C. A cycle.**
```
s = lambda i, dep: Stage(id=i, name="n", description="d", source_text="t", depends_on=dep)
ProcessModel(process_name="p", stages=[s(1, [2]), s(2, [1])])
```
Expected: `depends_on contains a cycle; declare loop-backs with rework_to`.

## Reading the output (from a real run on Windows)

Each failed experiment prints a block that looks like a crash. It is not. It is the schema doing its job. This is how to read it, using experiment A:

```
Traceback (most recent call last):                          <- Python's standard heading; ignore
  File "<python-input-1>", line 1, in <module>              <- the line you typed
  File ".venv\Lib\site-packages\pydantic\main.py", line 280 <- the library's internal path; ignore
pydantic_core._pydantic_core.ValidationError: 1 validation error for Stage     <- THE RESULT: a Stage was refused
  Value error, stage 1: 'probably the operator' hedges inside a name;          <- THE RULE, written in process.py
  put inferences in assumptions or ambiguities
  [type=value_error, input_value=...]                       <- technical detail of what was submitted
  For further information visit https://errors.pydantic.dev/...   <- a documentation link; ignore
```

The useful part is always the lines after `ValidationError`. For experiment B they are the field name `colour`, then `Extra inputs are not permitted`. For experiment C they are `depends_on contains a cycle; declare loop-backs with rework_to`.

Two things follow from a refusal. No object is created, so the bad data never enters the pipeline. And the same message is what a model receives in the retry prompt, which tells it exactly what to fix.

**Positive control:** remove the offending part and run the same line again. For A, use `actors=["the operator"]`. The stage is built without error and Python prints it. Only one word changed, and the rule is the only reason the outcome changed.

## Check yourself

1. Why are the scores integers from 1 to 5? *(A model cannot justify a percentage. The levels have defined meanings in the Analyst prompt.)*
2. How is a real loop, such as a failed quality check sending a lot back to an earlier stage, written down? *(With `rework_to`, giving the target stage and the trigger condition. Not with `depends_on`.)*
3. `human_only` appears in two lists. What is the difference? *(One says who checks; the other says where the AI action sits, and here there is none.)*
4. Which two checks on the Analyst's reply are not in the schemas? *(That every stage is covered, and the mandatory-oversight rule. Both are in `analyst.check_analysis`.)*

