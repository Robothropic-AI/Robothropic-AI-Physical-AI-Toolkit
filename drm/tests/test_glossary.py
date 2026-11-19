import json
from pathlib import Path

from drm.backend import bridge
from drm.backend.glossary import GLOSSARY, find_abbreviations, glossary_section
from drm.backend.render import render_markdown
from drm.backend.synthesizer import build_report
from drm.tests.test_synthesizer import ANALYSIS, FIXTURE, PROCESS


def test_finds_abbreviations_including_mixed_case_and_ignores_status_words():
    text = "PROVISIONAL. The PLC logs data (see SOP-12); QC compares against the CoA. Tier 1 JSON e-beam."
    assert find_abbreviations(text) == {"PLC", "SOP", "QC", "CoA"}


def test_glossary_lists_known_terms_sorted_and_flags_unknown_ones():
    section = glossary_section("QC and PLC and XYZQ appear here")
    assert section.index("**PLC**") < section.index("**QC**")
    assert "### Terms to confirm" in section and "- XYZQ" in section
    assert "XYZQ" not in "".join(GLOSSARY)  # never guessed


def test_multi_word_term_is_one_term_and_its_parts_are_not_flagged():
    text = "Options: PLC data export, or an OPC UA server or gateway."
    assert find_abbreviations(text) == {"PLC", "OPC UA"}
    section = glossary_section(text)
    assert "**OPC UA**" in section and "Terms to confirm" not in section


def test_plain_opc_is_still_defined_on_its_own():
    assert find_abbreviations("An OPC gateway") == {"OPC"}
    assert "**OPC**" in glossary_section("An OPC gateway")


def test_glossary_is_empty_without_abbreviations():
    assert glossary_section("plain words only") == ""


def test_every_definition_is_a_plain_sentence():
    for term, text in GLOSSARY.items():
        assert text.strip() and text[0].isupper() and len(text) > 20, term


def test_report_contains_glossary_with_the_terms_used():
    md = render_markdown(build_report(PROCESS, ANALYSIS))
    assert "## Glossary" in md and "**QC**: Quality control" in md and "**AI**:" in md
    assert "glossary at the end" in md
    assert md.index("## Limitations") < md.index("## Glossary")


def test_report_command_out_name_and_note(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("analysis.json").write_text(ANALYSIS.model_dump_json(), encoding="utf-8")
    out = tmp_path / "new" / "folder"
    code = bridge.main(["bridge", "report", str(FIXTURE), "analysis.json", "--oversight", "mandatory",
                        "--out", str(out), "--name", "optical_coating_line_report",
                        "--note", "Analyst reply from a manual run; one stray empty field removed by hand."])
    assert code == 0
    md = (out / "optical_coating_line_report.md").read_text(encoding="utf-8")
    assert "Provenance: Analyst reply from a manual run" in md and "## Glossary" in md
    assert json.loads((out / "optical_coating_line_report.json").read_text(encoding="utf-8"))["provisional"] is True
    assert not Path("drm_report.md").exists()  # nothing written to the current folder


def test_report_command_prints_full_paths_and_sizes(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    Path("analysis.json").write_text(ANALYSIS.model_dump_json(), encoding="utf-8")
    out = tmp_path / "r"
    assert bridge.main(["bridge", "report", str(FIXTURE), "analysis.json", "--out", str(out), "--name", "x"]) == 0
    text = capsys.readouterr().out
    assert str(out / "x.md") in text and str(out / "x.json") in text and "bytes" in text


def test_open_flag_opens_the_folder(tmp_path, monkeypatch):
    import os
    opened = []
    monkeypatch.setattr(os, "startfile", lambda folder: opened.append(folder), raising=False)
    monkeypatch.chdir(tmp_path)
    Path("analysis.json").write_text(ANALYSIS.model_dump_json(), encoding="utf-8")
    assert bridge.main(["bridge", "report", str(FIXTURE), "analysis.json", "--out", str(tmp_path / "o"), "--open"]) == 0
    assert opened == [str(tmp_path / "o")]

