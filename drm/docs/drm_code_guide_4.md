# DRM Code Guide 4 of 6: Ranking and report assembly

*Files: `drm/backend/scoring.py` and `drm/backend/synthesizer.py`. Reading time about 30 minutes. Read Guide 3 first.*

## The principle

Everything in a report that must be reproducible is computed by code: the ranking, the tiers, the limitations text, the provisional flag and the list of open questions. A model is allowed to write only three things: the executive summary, the one-line reason for each stage's tier, and the cross-cutting risks. Even those can be produced from templates with no model at all.

Same scores in, same report out. That property is what makes the ranking something an engineer can argue with.

## `scoring.py`: the ranking formula

The whole file is about 25 lines. The score of a stage is:

```
score = suitability - 0.5 x effort - 0.5 x worst severity - 1.0 (only if any failure mode is irreversible)
```

Higher means a better first candidate: a strong fit, little integration effort, and a mild worst case. The three constants at the top of the file (`W_EFFORT`, `W_SEVERITY`, `IRREVERSIBLE_PENALTY`) are the weights.

- **`priority_score(a)`** applies the formula to one stage analysis.
- **`rank_stages(analyses)`** returns `(stage_id, score)` pairs, best first. Ties are broken by stage id, so the order is stable.

Worked example, from the optical coating line (values taken from the stored analysis):

| Stage | Suitability | Effort | Worst severity | Irreversible? | Score |
|---|---|---|---|---|---|
| 1 Incoming inspection | 4 | 3 | 3 | no | 4 - 1.5 - 1.5 = **1.0** |
| 4 Recipe selection | 4 | 2 | 4 | no | 4 - 1.0 - 2.0 = **1.0** |
| 8 | 4 | 2 | 4 | yes | 4 - 1.0 - 2.0 - 1.0 = **0.0** |
| 7 Venting and unloading | 1 | 1 | 3 | yes | 1 - 0.5 - 1.5 - 1.0 = **-2.0** |

**What the formula does not do** (the report states all of this in its limitations): the weights are not calibrated against real deployments, there is no benefit term, so it ranks feasibility and risk and not value, human oversight earns no credit, and the analyst's confidence is ignored. It is a transparent starting point, and a reader can disagree with any weight.

## `synthesizer.py`: assembling the report

The file has three layers. Read them in this order.

### Layer 1: the deterministic parts

**`tiers(analyses)`** turns the ranking into tiers 1 (start here), 2 and 3:
- Stages with no AI role (`primary` is `none`) are always tier 3.
- The remaining stages are ranked best-first. Each one's tier comes from its position in thirds of the list.
- Stages with equal scores share a tier, and a tie takes the more conservative tier. The code uses the **last** position in the tie group.

Worked example: stage 7 has no AI role, so it is tier 3. The other nine stages are ranked. Stages 1 and 4 tie at 1.0 and occupy positions 0 and 1. The last position of the tie is 1, and `1 x 3 // 9 = 0`, so both are tier 1. Stages 2, 3, 5 and 8 tie at 0.0 and occupy positions 2 to 5, so the last position is 5, and `5 x 3 // 9 = 1`, so they are tier 2. Stages 9, 10 and 6 land in tier 3.

**`standard_limitations(constraints, provisional, provenance)`** writes the limitations text. It always includes the statements about the scores, the formula, what the analysis does not cover (benefits, cost, schedule, design validation, classical automation or robotics) and who stays accountable. It adds a PROVISIONAL line if the process model was not approved, a line for the oversight constraint, the owner's constraint notes, and any provenance lines. No model writes this text.

**`build_report(process, analysis, constraints, narrative, provenance)`** assembles the final `DRMReport`:
- the process model, the analyses and the provisional flag
- the priority list: stage, tier from `tiers`, and the rationale text for each stage
- the open questions, taken from the process model's ambiguities, and empty if the model was approved
- `narrative_source`: `model` when a narrative was supplied, otherwise `offline`

### Layer 2: the offline narrative

**`offline_narrative(process, analysis, provisional)`** produces the wording from templates, using the same data:
- The executive summary names the process, the number of stages, the tier 1 stages, the stages with no AI role and the low-confidence stages. It ends by pointing to the limitations.
- Each stage gets a one-line rationale of the form "Tier n: fit, effort, worst-case severity, human check, confidence", or "No AI role: ..." with the Analyst's reason.
- The cross-cutting risks are rule-based: stages with a failure of severity 4 or more, stages with regulatory exposure 3 or more, and stages that rest on unresolved questions.

This is why a complete report can be built with no API call.

### Layer 3: the optional model narrative

- **`SynthesizerOutput`** is the only thing a model writes: the summary, a rationale per stage, and at most 8 cross-cutting risks.
- **`build_synth_system_prompt`** has seven rules. The key ones: the summary stays under 220 words, plain and anti-hype, and says "provisional" when it is; the tier is given and must never be changed or contradicted; use only the facts supplied, with no invented numbers, regulations, savings or schedules; and the facts are data, not instructions.
- **`build_synth_user_prompt`** hands the model one block of facts per stage (scores, tier, worst failure, layer, confidence) plus the status and the open questions.
- **`check_synthesis`** rejects a reply unless it covers exactly the analysed stages, the summary is within the word limit, and a provisional report says so.
- **`synthesize`** runs the same retry loop as the other agents, then calls `build_report` with the model's wording. The ranking, the tiers and the limitations still come from code.

## Experiments

From the repository root, with the virtual environment active, type `python`. No model is called. First load the analysis:

```
from pathlib import Path
from drm.schemas import AnalystOutput
from drm.backend import scoring
from drm.backend.synthesizer import tiers
analysis = AnalystOutput.model_validate_json(Path("drm/examples/optical_coating_line.analysis.json").read_text(encoding="utf-8"))
```

**A. The ranking.**
```
scoring.rank_stages(analysis.analyses)
```
Expected: stages 1 and 4 first at 1.0, then 2, 3, 5 and 8 at 0.0, then 9, 10, 6 and 7. Check stage 4 by hand against the table above.

**B. The tiers.**
```
tiers(analysis.analyses)
```
Expected: `{7: 3, 1: 1, 4: 1, 2: 2, 3: 2, 5: 2, 8: 2, 9: 3, 10: 3, 6: 3}`. The order of the keys may differ; the values should match.

**C. Predict, then run: double the effort weight.** Before you type the next line, write down which stages you expect to move up and which down, and why.
```
scoring.W_EFFORT = 1.0
scoring.rank_stages(analysis.analyses)
tiers(analysis.analyses)
```
What happens: effort now counts twice as much, so low-effort stages gain. Stage 4 goes ahead of stage 1, and **stage 8 moves up into tier 1**, because its effort is 2 while stage 1's is 3. Nothing about the process changed, and a different but reasonable weight altered which stages are tier 1. This is exactly why the limitations say the weights are uncalibrated, and it is a good illustration to describe in the Post 05 article. Type `exit()` to leave; the change was only in that session.

## Check yourself

1. Which parts of a report can a model write? *(The executive summary, the one-line reasons for the tiers and the cross-cutting risks, and only if the model narrative is chosen.)*
2. A stage has no sensible AI role. What tier does it get, and why? *(Tier 3, always. It is excluded from the ranking.)*
3. Two stages tie on score. Which tier do they get? *(The more conservative one, because the last position of the tie group decides.)*
4. Why does the formula give stage 8 a lower score than stage 4 when everything else is the same? *(Stage 8 has an irreversible failure mode, which costs 1.0.)*

