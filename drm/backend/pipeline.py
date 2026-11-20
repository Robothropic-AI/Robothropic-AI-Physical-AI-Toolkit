"""One command from a numbered process description to a JSON and Markdown report.

    python -m drm.backend.pipeline <input> [--oversight mandatory|recommended|unspecified]
        [--approval approval.json] [--narrative model|offline] [--out FOLDER] [--name BASE] [--open]

<input> is either a process description (numbered stages, .md or .txt), which the Decomposer turns into a
process model, or a saved process model (.json), which skips the Decomposer.

Stages: Decomposer -> Analyst -> Synthesizer. Every stage validates the model's reply and retries on failure
(see decomposer.py, analyst.py, synthesizer.py). Ranking, tiers, limitations and the provisional flag are
computed in code. With --narrative offline the Synthesizer's wording comes from templates and no third call
is made.

The report is PROVISIONAL unless an approval file is given. The approval file names the human approver and
answers every open question of the process model:
    {"approved_by": "Name", "resolutions": [{"question": "<exact ambiguity text>", "answer": "..."}]}
Because the questions come from the Decomposer, the usual order is: run once, read the open questions in the
report, write the approval file, then run again from the saved process model (.json) with --approval.

This command calls the live Claude API and needs ANTHROPIC_API_KEY. Model settings are in config.py.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from drm.backend import config
from drm.backend.analyst import analyse, is_provisional
from drm.backend.bridge import announce, write_report
from drm.backend.decomposer import decompose
from drm.backend.synthesizer import build_report, standard_limitations, synthesize
from drm.schemas import (AnalystOutput, ApprovedProcessModel, Constraints, DRMReport, HumanOversight,
                         ProcessModel, Resolution)

NARRATIVES = ("model", "offline")


@dataclass
class PipelineResult:
    process: ProcessModel | ApprovedProcessModel
    analysis: AnalystOutput
    report: DRMReport


def apply_approval(model: ProcessModel, approval: dict) -> ApprovedProcessModel:
    """Wrap a process model in a human approval. Raises ValueError unless every question is answered."""
    resolutions = [Resolution(question=r["question"], answer=r["answer"]) for r in approval.get("resolutions", [])]
    return ApprovedProcessModel(process=model, approved_by=approval.get("approved_by", ""),
                                resolutions=resolutions)


def run_pipeline(source: str | ProcessModel, constraints: Constraints | None = None,
                 approval: dict | None = None, narrative: str = "model", client=None,
                 log=lambda message: None) -> PipelineResult:
    """Run the three agents. `source` is the process description text or an already built ProcessModel."""
    if narrative not in NARRATIVES:
        raise ValueError(f"narrative must be one of {NARRATIVES}")
    constraints = constraints or Constraints()
    if isinstance(source, ProcessModel):
        model = source
        log("Decomposer: skipped (a saved process model was given)")
    else:
        log("Decomposer: reading the process description ...")
        model = decompose(source, client=client)
        log(f"Decomposer: done ({len(model.stages)} stages, {len(model.ambiguities)} open questions)")
    process: ProcessModel | ApprovedProcessModel = apply_approval(model, approval) if approval else model

    log("Analyst: scoring every stage ...")
    analysis = analyse(process, constraints, client=client)
    log(f"Analyst: done ({len(analysis.analyses)} stages scored)")

    provenance = [f"Produced by the DRM pipeline (model {config.MODEL}, effort {config.EFFORT}); "
                  "no hand edits."]
    if narrative == "model":
        log("Synthesizer: writing the report wording ...")
        report = synthesize(process, analysis, constraints, client=client)
        report = report.model_copy(update={"limitations": standard_limitations(
            constraints, is_provisional(process), provenance)})
    else:
        log("Synthesizer: building the report from templates (no model call) ...")
        report = build_report(process, analysis, constraints, provenance=provenance)
    log("Synthesizer: done")
    return PipelineResult(process=process, analysis=analysis, report=report)


def write_outputs(result: PipelineResult, out_dir: str, name: str) -> list[str]:
    """Write <name>.md and <name>.json (the report), plus the process model and the analysis as JSON."""
    folder = os.path.abspath(out_dir)
    os.makedirs(folder, exist_ok=True)
    paths = write_report(result.report, folder, name)
    model = result.process.process if isinstance(result.process, ApprovedProcessModel) else result.process
    extras = {f"{name}.processmodel.json": model.model_dump_json(indent=2),
              f"{name}.analysis.json": result.analysis.model_dump_json(indent=2)}
    for filename, text in extras.items():
        path = os.path.join(folder, filename)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        paths.append(path)
    return paths


def _option(args: list[str], flag: str) -> str | None:
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else None


USAGE = ("usage: python -m drm.backend.pipeline <input> [--oversight mandatory|recommended|unspecified] "
         "[--approval FILE] [--narrative model|offline] [--out FOLDER] [--name BASE] [--open]\n"
         "<input> is a numbered process description (.md or .txt) or a saved process model (.json).")


def main(argv: list[str], client=None) -> int:
    """Return 0 on success, 1 if the pipeline stopped, 2 for a usage or setup problem."""
    args = argv[1:]
    options = {k: _option(args, k) for k in ("--oversight", "--approval", "--narrative", "--out", "--name")}
    values = {v for v in options.values() if v}
    positional = [a for a in args if not a.startswith("--") and a not in values]
    if len(positional) != 1:
        print(USAGE)
        return 2
    source_path = positional[0]
    oversight = options["--oversight"] or HumanOversight.UNSPECIFIED.value
    narrative = options["--narrative"] or "model"
    if oversight not in {o.value for o in HumanOversight} or narrative not in NARRATIVES:
        print(USAGE)
        return 2
    if not os.path.exists(source_path):
        print(f"Input file not found: {source_path}")
        return 2
    if client is None:
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("ANTHROPIC_API_KEY is not set. This command calls the Claude API. Without API credit, "
                  "use the manual bridge (python -m drm.backend.bridge).")
            return 2
        import anthropic
        client = anthropic.Anthropic()

    try:
        text = Path(source_path).read_text(encoding="utf-8-sig")
        source: str | ProcessModel = (ProcessModel.model_validate_json(text)
                                      if source_path.lower().endswith(".json") else text)
        approval = (json.loads(Path(options["--approval"]).read_text(encoding="utf-8-sig"))
                    if options["--approval"] else None)
        print(f"Model {config.MODEL}, effort {config.EFFORT}; human oversight {oversight}.")
        result = run_pipeline(source, Constraints(human_oversight=HumanOversight(oversight)), approval,
                              narrative, client, log=print)
        paths = write_outputs(result, options["--out"] or "report_out",
                              options["--name"] or Path(source_path).stem)
    except Exception as exc:  # a failed run must end with a clear message, not a stack trace
        print(f"Pipeline stopped: {type(exc).__name__}: {str(exc)[:600]}")
        return 1
    announce(paths, "--open" in args, "PROVISIONAL report" if result.report.provisional else "FINAL report")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))

