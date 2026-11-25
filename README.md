# Robothropic AI - Physical AI Toolkit


**Agentic AI as the cognitive and planning layer for physical robots. From factory floors to planetary surfaces.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Stack: Python + Pydantic v2](https://img.shields.io/badge/Stack-Python%20%2B%20Pydantic%20v2-green.svg)](https://docs.pydantic.dev)
[![LLM: Claude API](https://img.shields.io/badge/LLM-Claude%20API-orange.svg)](https://www.anthropic.com)
[![Publication: Robothropic AI on Substack](https://img.shields.io/badge/Publication-Substack-red.svg)](https://robothropicai.substack.com)

---

## What This Is

**Robothropic AI** is an agentic AI robotics platform — open-source software infrastructure for physical AI systems across all robot form factors and deployment environments: industrial automation, advanced manufacturing, space operations, and beyond.

This repository is the engineering complement to the [Robothropic AI publication](https://robothropicai.substack.com). Every build here has a companion analytical article, and every build ships with its tests.

The thesis is precise: **the agentic loop — perceive, reason, act, observe, repeat — is the foundational software architecture for physical AI at every scale.** The parameters change across robot bodies and environments. The architectural pattern does not.

---

## The Architecture

Every build in this toolkit is an instance of the same four-component pattern:

```
┌─────────────────────────────────────────────────────┐
│                  AGENTIC LOOP                       │
│                                                     │
│  ┌──────────────┐    ┌──────────────┐               │
│  │   Reasoning  │───▶│    Memory    │               │
│  │   Engine     │    │  (state,     │               │
│  │  (Claude API)│◀───│  context,    │               │
│  └──────┬───────┘    │  retrieval)  │               │
│         │            └──────────────┘               │
│         ▼                                           │
│  ┌──────────────┐    ┌──────────────┐               │
│  │     Tools    │───▶│Orchestration │               │
│  │  (APIs, DB,  │    │  (control    │               │
│  │  sensors,    │◀───│   flow,      │               │
│  │  actuators)  │    │  escalation) │               │
│  └──────────────┘    └──────────────┘               │
│                                                     │
│  Fast layer (onboard) ←──────→ Slow layer (ground)  │
└─────────────────────────────────────────────────────┘
```

**Two-layer deployment architecture** — validated by the JPL/Anthropic Perseverance rover deployment (December 2025, first AI-planned drives on Mars):
- **Fast layer**: onboard, real-time, low-stakes, reversible decisions
- **Slow layer**: ground-side, verified, human-reviewed, high-stakes planning

AI for throughput. Human expert for accountability.

---

## Repository Structure

What is in the repository today:

```
Robothropic-AI-Physical-AI-Toolkit/
│
├── README.md
├── requirements.txt
├── LICENSE                       # Apache 2.0
│
└── /drm                          # Deployment Readiness Mapper (command-line release)
    ├── README.md                 # usage, approval, evidence, limitations
    ├── /schemas                  # Pydantic models and the rules they enforce
    ├── /backend                  # decomposer, analyst, synthesizer, scoring, render,
    │                             #   glossary, pipeline, bridge, config
    ├── /tests                    # 86 tests; stand-in clients, no key, no network
    ├── /examples                 # worked inputs and outputs
    └── /docs                     # code guides 1 to 4
```

Planned, not yet in the repository:

- `/drm`: an API layer (FastAPI) and a frontend (React / TypeScript)
- `/signals`: one folder per Robothropic Signal post that has code
- `/lectures`: one folder per Robothropic Lecture with a code prototype (`/lectures/[NN-slug]/`)
- `/notebooks`: Jupyter notebooks for analytical pieces

---

## Current Build: Deployment Readiness Mapper (DRM)

**Status**: command-line release. The API layer and the frontend are planned, not built. Nothing has yet been run against the live API; see "What has been run" below.

The DRM is a three-agent pipeline that takes a structured description of an industrial or physical AI process and returns a structured analysis across three dimensions:

| Dimension | What it answers |
|-----------|----------------|
| **Intervention Opportunities** | Where can an AI agent act? Classify each stage: perception, reasoning, execution, communication |
| **Integration Surface** | What does connecting AI here actually require? Data, interfaces, latency, human-in-the-loop |
| **Risk Profile** | What are the failure modes? Severity, reversibility, regulatory exposure |

### Pipeline

```
Structured process input (numbered stages)
        │
        ▼
[ Decomposer Agent ]  →  parse stages, actors, systems, records, dependencies, open questions
        │
        ▼
[ Analyst Agent ]     →  score each stage across all three dimensions (one call for the whole process)
        │
        ▼
[ Synthesizer Agent ] →  priority map and tiers (computed in code) + report wording
        │
        ▼
Output: structured JSON + human-readable Markdown report
```

Every model reply is validated against strict schemas and retried on failure. Ranking, tiers, the limitations text and the PROVISIONAL flag are computed in code, not written by a model.

### What has been run

- 86 tests pass. They use stand-in clients: no key and no network.
- The model calls so far were made by hand through the Claude app, using the manual bridge. The one-command pipeline has not been run against the live API.
- The worked example (an anti-reflective coating line) is illustrative, with no plant data behind it.

The evidence and the limits are stated in [`drm/README.md`](drm/README.md) and in Post 05 of the publication.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Claude API (`claude-sonnet-5-5`, set in `drm/backend/config.py`) |
| Backend | Python, Pydantic v2 (FastAPI layer planned) |
| Frontend | Planned: React + TypeScript |
| Output | Structured JSON + Markdown |
| License | Apache 2.0 |

### Quick start

Tested on Python 3.12 and 3.14.

```
pip install -r requirements.txt
python -m pytest drm/tests -q
```

Usage, the approval step and the manual bridge are in [`drm/README.md`](drm/README.md).

The DRM is the first module. Subsequent modules extend the toolkit as the platform grows.

---

## Robothropic Signal (planned)

Alongside the main builds, Signals will be fast posts triggered by a notable paper, deployment or field development, and a way to look for real engineering examples to bring into the toolkit. A Signal that comes with code will live in `/signals/[slug]/` with a short README that links to the companion article. A Signal ships when its insight is ready, not on a fixed schedule.

---

## Robothropic Lecture (planned)

A Lecture is an in-depth article on one research paper or development in robotics and physical AI, with a minimal code prototype where it fits, in `/lectures/[NN-slug]/`. A webcast explainer is planned for each Lecture; the platform and format are not decided. Lectures start after the Founding Series ends, and a Lecture ships when its code runs and its analysis is sound.

---

## Application Domains

This toolkit is domain-agnostic at the architecture level. Current and planned application domains:

- **Industrial Robotics**: factory floors, advanced manufacturing, logistics, process automation
- **Space Operations**: planetary exploration, on-orbit systems, autonomous navigation
- **Advanced Manufacturing**: quality inspection, assembly, process control
- **Physical AI Infrastructure**: deployment readiness, integration surface analysis, agent observability

---

## Publication

Every build has a companion article on the [Robothropic AI Substack](https://robothropicai.substack.com) covering:
- The problem being solved
- The architecture and design decisions
- A worked example
- The code walkthrough

The publication and the repository are co-developed. The writing explains the engineering. The engineering validates the writing.

---

## Collaboration

Robothropic AI operates as a **co-innovation partner** for organisations working on physical AI deployment — industrial, space, and advanced manufacturing. If the problems this toolkit addresses map to problems you are working on, the conversation starts at [robothropicai.substack.com](https://robothropicai.substack.com) or through the publication directly.

Contributions, issues, and technical discussions are welcome via GitHub.

---

## License

[Apache License 2.0](LICENSE)

---

*Built with Anthropic Claude. Published at [robothropicai.substack.com](https://robothropicai.substack.com).*

