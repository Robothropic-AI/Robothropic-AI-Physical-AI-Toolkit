"""General-purpose definitions of abbreviations that may be new to readers of a DRM report.

Definitions are deliberately generic: a plant may use a term more specifically. Abbreviations
found in a report but missing here are listed as "terms to confirm" and never guessed.
"""
from __future__ import annotations

import re

GLOSSARY: dict[str, str] = {
    "AI": "Artificial intelligence: software that performs tasks that normally need human judgment, "
          "such as recognising defects in images or recommending a setting.",
    "API": "Application programming interface: a defined way for one software system to request data "
           "from, or send data to, another.",
    "CoA": "Certificate of analysis: a supplier's document stating the tested properties of a delivered material.",
    "ERP": "Enterprise resource planning: business software that manages orders, materials and work orders.",
    "HMI": "Human-machine interface: the screen or panel an operator uses to see and control a machine.",
    "ID": "Identifier: a code that uniquely names an item, such as a lot or a lens.",
    "MES": "Manufacturing execution system: software that tracks and records what happens on the production "
           "floor, including batch records.",
    "ML": "Machine learning: methods in which software learns patterns from example data.",
    "OCR": "Optical character recognition: software that reads printed or handwritten text from images.",
    "OPC": "A family of industrial standards for exchanging data between control equipment and software "
           "(originally 'OLE for Process Control').",
    "OPC UA": "OPC Unified Architecture: the current, vendor-neutral OPC standard (IEC 62541) for reading data "
              "from industrial equipment through one common interface.",
    "PLC": "Programmable logic controller: a rugged industrial computer that runs a machine's control "
           "sequences, such as opening shutters or holding a deposition rate.",
    "QA": "Quality assurance: the function that sets up and oversees quality systems and often makes the "
          "batch-release decision.",
    "QC": "Quality control: checks that a product or batch meets its specification, such as measuring or "
          "inspecting samples.",
    "QMS": "Quality management system: the documented procedures and records through which a company "
           "controls quality.",
    "SCADA": "Supervisory control and data acquisition: a system that monitors and controls industrial "
             "equipment from a central point.",
    "SOP": "Standard operating procedure: a written, approved description of how a task must be done.",
    "SPC": "Statistical process control: using statistical charts to monitor whether a process stays stable.",
    "UV": "Ultraviolet: light of shorter wavelength than visible light.",
    "VLA": "Vision-language-action model: an AI model that turns images and instructions into robot actions.",
    "VLM": "Vision-language model: an AI model that processes images together with text.",
}

# Words in capitals that are report status labels or file formats, not abbreviations to explain.
_NOT_ABBREVIATIONS = {"PROVISIONAL", "FINAL", "JSON"}
# A token with at least two capital letters, 2-8 characters long (covers PLC, QC and CoA).
_TOKEN = re.compile(r"\b(?=[A-Za-z0-9]{2,8}\b)[A-Za-z0-9]*[A-Z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*\b")


def find_abbreviations(text: str) -> set[str]:
    """Abbreviations in `text`. Known multi-word terms (such as "OPC UA") are matched first, as one
    term each, so their parts are not looked up or flagged separately."""
    found: set[str] = set()
    for phrase in sorted((k for k in GLOSSARY if " " in k), key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(phrase)}\b")
        if pattern.search(text):
            found.add(phrase)
            text = pattern.sub(" ", text)
    found |= {t for t in _TOKEN.findall(text) if t not in _NOT_ABBREVIATIONS}
    return found


def glossary_section(text: str) -> str:
    """Markdown glossary for the abbreviations found in `text`; empty if there are none."""
    found = sorted(find_abbreviations(text), key=str.lower)
    if not found:
        return ""
    known = [a for a in found if a in GLOSSARY]
    unknown = [a for a in found if a not in GLOSSARY]
    lines = ["## Glossary", "",
             "General definitions of the abbreviations used in this report. A plant may use some of these "
             "terms more specifically.", ""]
    lines += [f"- **{a}**: {GLOSSARY[a]}" for a in known]
    if unknown:
        lines += ["", "### Terms to confirm", "",
                  "These abbreviations appear in the report but have no standard definition on file. "
                  "Confirm their meaning with the process owner:", ""]
        lines += [f"- {a}" for a in unknown]
    return "\n".join(lines) + "\n"


