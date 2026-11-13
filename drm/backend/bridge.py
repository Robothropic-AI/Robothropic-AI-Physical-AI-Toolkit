"""Manual bridge: run the Decomposer's prompt by hand when no API credit is available.

Workflow (PowerShell, from the repo root, venv active):
  1. python -m drm.backend.bridge prompt drm/examples/optical_coating_line.md
        -> writes bridge_prompt.txt; paste its whole contents into a fresh Claude chat.
  2. Copy Claude's reply, then:  Get-Clipboard | Set-Content bridge_reply.json -Encoding utf8
  3. python -m drm.backend.bridge check drm/examples/optical_coating_line.md
        -> applies the same schema and traceability checks as the live Decomposer.
        On failure it writes bridge_retry_prompt.txt to paste back into the same chat.
"""
from __future__ import annotations

import sys

from drm.backend.decomposer import (build_retry_prompt, build_system_prompt,
                                    build_user_prompt, parse_and_check)
from drm.schemas import ProcessModel

PROMPT_FILE = "bridge_prompt.txt"
REPLY_FILE = "bridge_reply.json"
RETRY_FILE = "bridge_retry_prompt.txt"


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


def summarise(model: ProcessModel) -> str:
    rows = [f"Process: {model.process_name}", ""]
    for s in model.stages:
        loops = [f"->{e.to} if {e.when}" for e in s.rework_to]
        rows.append(f"{s.id:>2}  {s.name[:44]:<44} depends_on={s.depends_on} rework={loops}")
        rows.append(f"      actors={s.actors} inputs={s.inputs} outputs={s.outputs}")
    rows += ["", f"Assumptions ({len(model.assumptions)}):"] + [f"  - {a}" for a in model.assumptions]
    rows += ["", f"Ambiguities ({len(model.ambiguities)}):"] + [f"  - {a}" for a in model.ambiguities]
    return "\n".join(rows)


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
        reply = _read(argv[3] if len(argv) > 3 else REPLY_FILE)
        model, error = check_reply(process_text, reply)
        if model is not None:
            print("VALID: schema and traceability checks passed.\n")
            print(summarise(model))
            return 0
        with open(RETRY_FILE, "w", encoding="utf-8") as fh:
            fh.write(build_retry_prompt(process_text, reply, error))
        print("INVALID:\n" + error[:1500])
        print(f"\nWrote {RETRY_FILE}. Paste it into the same chat, save the new reply, and check again.")
        return 1
    print("usage:\n  python -m drm.backend.bridge prompt <process_file>\n"
          "  python -m drm.backend.bridge check <process_file> [reply_file]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

