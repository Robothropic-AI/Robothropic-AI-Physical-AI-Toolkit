"""Manual bridge: run the Decomposer's prompt by hand when no API credit is available.

Workflow (PowerShell, from the repo root, venv active):
  1. python -m drm.backend.bridge prompt <process_file>
        -> writes bridge_prompt.txt; paste its whole contents into a fresh Claude chat.
  2. Copy Claude's reply with the chat's copy button, and copy nothing else afterwards.
  3. python -m drm.backend.bridge check <process_file> --clipboard
        -> reads the reply straight from the clipboard (no file or editor needed) and
           applies the same schema and traceability checks as the live Decomposer.
        Alternatively: check <process_file> <reply_file> reads a saved file instead.
  On failure the checker shows what it actually read, and writes bridge_retry_prompt.txt.
"""
from __future__ import annotations

import subprocess
import sys

from drm.backend.analyst import (build_analyst_retry_prompt, build_analyst_system_prompt,
                                 build_analyst_user_prompt, is_provisional, parse_and_check_analysis)
from drm.backend.analyst import check_analysis
from drm.backend.decomposer import (_extract_json, build_retry_prompt, build_system_prompt,
                                    build_user_prompt, parse_and_check)
from drm.backend.render import render_markdown
from drm.backend.scoring import priority_score, rank_stages
from drm.backend.synthesizer import (SynthesizerOutput, build_report, build_synth_retry_prompt,
                                     build_synth_system_prompt, build_synth_user_prompt, parse_and_check_synthesis)
from drm.schemas import (AnalystOutput, ApprovedProcessModel, Constraints, HumanOversight,
                         ProcessModel)

PROMPT_FILE = "bridge_prompt.txt"
REPLY_FILE = "bridge_reply.json"
RETRY_FILE = "bridge_retry_prompt.txt"
ANALYSIS_PROMPT_FILE = "bridge_analysis_prompt.txt"
ANALYSIS_REPLY_FILE = "bridge_analysis_reply.json"
ANALYSIS_RETRY_FILE = "bridge_analysis_retry_prompt.txt"
REPORT_PROMPT_FILE = "bridge_report_prompt.txt"
REPORT_REPLY_FILE = "bridge_report_reply.json"
REPORT_RETRY_FILE = "bridge_report_retry_prompt.txt"
REPORT_MD = "drm_report.md"
REPORT_JSON = "drm_report.json"


def make_prompt(process_text: str) -> str:
    return (build_system_prompt()
            + "\nNow process the input below and reply with the JSON object only.\n\n"
            + build_user_prompt(process_text))


def check_reply(process_text: str, reply_text: str) -> tuple[ProcessModel | None, str]:
    """Return (model, "") on success or (None, error message) on failure."""
    try:
        return parse_and_check(reply_text, process_text), ""
    except ValueError as exc:
        return None, str(exc)


def describe(text: str, limit: int = 300) -> str:
    """Say what was read, so a wrong clipboard or file is obvious at a glance."""
    head = " ".join(text[:limit].split())
    return f"Read {len(text)} characters. It starts with: {head!r}"


def summarise(model: ProcessModel) -> str:
    rows = [f"Process: {model.process_name}", ""]
    for s in model.stages:
        loops = [f"->{e.to} if {e.when}" for e in s.rework_to]
        rows.append(f"{s.id:>2}  {s.name[:44]:<44} depends_on={s.depends_on} rework={loops}")
        rows.append(f"      actors={s.actors} systems={s.systems} records={s.records}")
        rows.append(f"      inputs={s.inputs} outputs={s.outputs}")
    rows += ["", f"Assumptions ({len(model.assumptions)}):"] + [f"  - {a}" for a in model.assumptions]
    rows += ["", f"Ambiguities ({len(model.ambiguities)}):"] + [f"  - {a}" for a in model.ambiguities]
    return "\n".join(rows)


def load_process(path: str) -> ProcessModel | ApprovedProcessModel:
    """Load a saved ProcessModel, or an ApprovedProcessModel (recognised by its 'process' key)."""
    text = _read(path)
    if '"approved_by"' in text:
        return ApprovedProcessModel.model_validate_json(text)
    return ProcessModel.model_validate_json(text)


def make_analysis_prompt(process, constraints: Constraints | None = None) -> str:
    return (build_analyst_system_prompt(constraints)
            + "\nNow analyse the process below and reply with the JSON object only.\n\n"
            + build_analyst_user_prompt(process))


def check_analysis_reply(process, reply_text: str,
                         constraints: Constraints | None = None) -> tuple[AnalystOutput | None, str]:
    try:
        return parse_and_check_analysis(reply_text, process, constraints), ""
    except ValueError as exc:
        return None, str(exc)


def summarise_analysis(process, output: AnalystOutput) -> str:
    model = process.process if isinstance(process, ApprovedProcessModel) else process
    names = {s.id: s.name for s in model.stages}
    status = ("PROVISIONAL (the process model is not yet approved; see its open ambiguities)"
              if is_provisional(process) else "FINAL (approved process model)")
    rows = [f"Analysis of: {model.process_name}", f"Status: {status}", "",
            " id  stage                                 AI role        fit effort sev  reg  human_in_loop   layer  conf"]
    for a in sorted(output.analyses, key=lambda x: x.stage_id):
        sev = max(f.severity for f in a.risk.failure_modes)
        rows.append(f"{a.stage_id:>3}  {names[a.stage_id][:36]:<36}  {a.intervention.primary.value:<13} "
                    f"{a.intervention.suitability:>3} {a.integration.effort:>6} {sev:>3} {a.risk.regulatory_exposure:>4}  "
                    f"{a.integration.human_in_loop.value:<14}  {a.layer_placement.value:<5}  {a.confidence.value}")
    rows += ["", "Ranking, best first candidate to start with (deterministic, from scoring.py; weights uncalibrated):"]
    for sid, score in rank_stages(output.analyses):
        rows.append(f"  {score:>5.1f}  stage {sid}: {names[sid]}")
    return "\n".join(rows)


def _option(args: list[str], name: str) -> str | None:
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else None


def _constraints(args: list[str]) -> Constraints:
    value = _option(args, "--oversight")
    return Constraints(human_oversight=HumanOversight(value)) if value else Constraints()


def load_analysis(path: str) -> AnalystOutput:
    return AnalystOutput.model_validate(_extract_json(_read(path)))


def _report_inputs(args: list[str]):
    """Parse: <processmodel.json> <analysis.json> [reply_file] [--clipboard] [--oversight X]
    [--out FOLDER] [--name BASENAME] [--note TEXT]."""
    opts = {k: _option(args, k) for k in ("--oversight", "--out", "--name", "--note")}
    values = {v for v in opts.values() if v}
    positional = [a for a in args if not a.startswith("--") and a not in values]
    return positional, "--clipboard" in args, _constraints(args), opts


def write_report(report, out_dir: str | None = None, name: str | None = None) -> list[str]:
    """Write <name>.md and <name>.json into out_dir (default: current folder).

    Returns the full paths written, after checking that each file exists and is not empty."""
    import os
    folder = os.path.abspath(out_dir or ".")
    os.makedirs(folder, exist_ok=True)
    base = name or "drm_report"
    paths = [os.path.join(folder, base + ".md"), os.path.join(folder, base + ".json")]
    contents = [render_markdown(report), report.model_dump_json(indent=2)]
    for path, text in zip(paths, contents):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            raise RuntimeError(f"could not write {path}")
    return paths


def announce(paths: list[str], open_folder: bool, kind: str) -> None:
    """Say exactly where the files are, and optionally open that folder."""
    import os
    print(f"{kind}. Files written:")
    for path in paths:
        print(f"  {path}  ({os.path.getsize(path)} bytes)")
    if open_folder and hasattr(os, "startfile"):
        os.startfile(os.path.dirname(paths[0]))


def read_clipboard() -> str:
    """Read the Windows clipboard through PowerShell (no extra Python package needed)."""
    cmd = ["powershell", "-NoProfile", "-Command",
           "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError("--clipboard needs PowerShell (Windows); use a reply file instead") from exc
    if result.returncode != 0:
        raise RuntimeError(f"could not read the clipboard: {result.stderr.strip()[:200]}")
    return result.stdout


def _read(path: str) -> str:
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        return fh.read()


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) >= 3 and argv[1] == "prompt":
        with open(PROMPT_FILE, "w", encoding="utf-8") as fh:
            fh.write(make_prompt(_read(argv[2])))
        print(f"Wrote {PROMPT_FILE}. Paste its whole contents into a fresh Claude chat.")
        return 0
    if len(argv) >= 3 and argv[1] == "check":
        process_text = _read(argv[2])
        source = argv[3] if len(argv) > 3 else REPLY_FILE
        if source == "--clipboard":
            reply = read_clipboard()
            with open(REPLY_FILE, "w", encoding="utf-8") as fh:
                fh.write(reply)
        else:
            reply = _read(source)
        print(describe(reply) + "\n")
        model, error = check_reply(process_text, reply)
        if model is not None:
            print("VALID: schema and traceability checks passed.\n")
            print(summarise(model))
            return 0
        with open(RETRY_FILE, "w", encoding="utf-8") as fh:
            fh.write(build_retry_prompt(process_text, reply, error))
        print("INVALID:\n" + error[:1500])
        print(f"\nWrote {RETRY_FILE}. Paste it into the same chat, copy the new reply, and check again.")
        return 1
    if len(argv) >= 3 and argv[1] == "analysis-prompt":
        constraints = _constraints(argv[3:])
        with open(ANALYSIS_PROMPT_FILE, "w", encoding="utf-8") as fh:
            fh.write(make_analysis_prompt(load_process(argv[2]), constraints))
        print(f"Wrote {ANALYSIS_PROMPT_FILE}. Paste its whole contents into a fresh Claude chat.")
        return 0
    if len(argv) >= 3 and argv[1] == "analysis-check":
        process = load_process(argv[2])
        constraints = _constraints(argv[3:])
        rest = [a for a in argv[3:] if a != "--oversight" and a != _option(argv[3:], "--oversight")]
        source = rest[0] if rest else ANALYSIS_REPLY_FILE
        if source == "--clipboard":
            reply = read_clipboard()
            with open(ANALYSIS_REPLY_FILE, "w", encoding="utf-8") as fh:
                fh.write(reply)
        else:
            reply = _read(source)
        print(describe(reply) + "\n")
        output, error = check_analysis_reply(process, reply, constraints)
        if output is not None:
            print("VALID: schema, stage coverage and constraint checks passed.\n")
            print(summarise_analysis(process, output))
            return 0
        with open(ANALYSIS_RETRY_FILE, "w", encoding="utf-8") as fh:
            fh.write(build_analyst_retry_prompt(process, reply, error))
        print("INVALID:\n" + error[:1500])
        print(f"\nWrote {ANALYSIS_RETRY_FILE}. Paste it into the same chat, copy the new reply, and check again.")
        return 1
    if len(argv) >= 4 and argv[1] == "report":
        positional, _, constraints, opts = _report_inputs(argv[2:])
        process, analysis = load_process(positional[0]), load_analysis(positional[1])
        try:
            check_analysis(analysis, process, constraints)
            report = build_report(process, analysis, constraints,
                                  provenance=[opts["--note"]] if opts["--note"] else None)
        except ValueError as exc:
            print("The analysis does not fit this process or its constraints:\n" + str(exc)[:1500])
            return 1
        paths = write_report(report, opts["--out"], opts["--name"])
        announce(paths, "--open" in argv, "Report built with offline wording (no model involved)")
        print(f"Status: {'PROVISIONAL' if report.provisional else 'FINAL'}; "
              f"tier 1: {[p.stage_id for p in report.priorities if p.tier == 1]}")
        return 0
    if len(argv) >= 4 and argv[1] == "report-prompt":
        positional, _, constraints, _opts = _report_inputs(argv[2:])
        process, analysis = load_process(positional[0]), load_analysis(positional[1])
        with open(REPORT_PROMPT_FILE, "w", encoding="utf-8") as fh:
            fh.write(build_synth_system_prompt()
                     + "\nNow write the wording for the facts below and reply with the JSON object only.\n\n"
                     + build_synth_user_prompt(process, analysis, constraints))
        print(f"Wrote {REPORT_PROMPT_FILE}. Paste its whole contents into a fresh Claude chat.")
        return 0
    if len(argv) >= 4 and argv[1] == "report-check":
        positional, clipboard, constraints, opts = _report_inputs(argv[2:])
        process, analysis = load_process(positional[0]), load_analysis(positional[1])
        if clipboard:
            reply = read_clipboard()
            with open(REPORT_REPLY_FILE, "w", encoding="utf-8") as fh:
                fh.write(reply)
        else:
            reply = _read(positional[2] if len(positional) > 2 else REPORT_REPLY_FILE)
        print(describe(reply) + "\n")
        try:
            narrative = parse_and_check_synthesis(reply, analysis, is_provisional(process))
            report = build_report(process, analysis, constraints, narrative,
                                  provenance=[opts["--note"]] if opts["--note"] else None)
        except ValueError as exc:
            user = build_synth_user_prompt(process, analysis, constraints)
            with open(REPORT_RETRY_FILE, "w", encoding="utf-8") as fh:
                fh.write(build_synth_retry_prompt(user, reply, str(exc)))
            print("INVALID:\n" + str(exc)[:1500])
            print(f"\nWrote {REPORT_RETRY_FILE}. Paste it into the same chat, copy the new reply, and check again.")
            return 1
        paths = write_report(report, opts["--out"], opts["--name"])
        announce(paths, "--open" in argv, "VALID. Report built with model wording, checked against the data")
        return 0
    print("usage:\n  python -m drm.backend.bridge prompt <process_file>\n"
          "  python -m drm.backend.bridge check <process_file> [--clipboard | reply_file]\n"
          "  python -m drm.backend.bridge analysis-prompt <processmodel.json> [--oversight mandatory|recommended]\n"
          "  python -m drm.backend.bridge analysis-check <processmodel.json> [--clipboard | reply_file] [--oversight ...]\n"
          "  python -m drm.backend.bridge report <processmodel.json> <analysis.json> [--oversight ...] [--out FOLDER] [--name BASE] [--note TEXT] [--open]   (offline, no model)\n"
          "  python -m drm.backend.bridge report-prompt <processmodel.json> <analysis.json> [--oversight ...]\n"
          "  python -m drm.backend.bridge report-check <processmodel.json> <analysis.json> [--clipboard | reply_file] [--oversight ...]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
