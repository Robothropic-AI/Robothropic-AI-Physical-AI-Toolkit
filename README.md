# Robothropic AI - Physical AI Toolkit


**Agentic AI as the cognitive and planning layer for physical robots. From factory floors to planetary surfaces.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Stack: FastAPI + Pydantic v2](https://img.shields.io/badge/Stack-FastAPI%20%2B%20Pydantic%20v2-green.svg)](https://fastapi.tiangolo.com)
[![LLM: Claude API](https://img.shields.io/badge/LLM-Claude%20API-orange.svg)](https://www.anthropic.com)
[![Publication: Robothropic AI on Substack](https://img.shields.io/badge/Publication-Substack-red.svg)](https://robothropicai.substack.com)

---

## What This Is

**Robothropic AI** is an agentic AI robotics platform — open-source software infrastructure for physical AI systems across all robot form factors and deployment environments: industrial automation, advanced manufacturing, space operations, and beyond.

This repository is the engineering complement to the [Robothropic AI publication](https://robothropicai.substack.com). Every build here has a companion analytical article. Every article has working code.

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

```
physical-ai-toolkit/
│
├── README.md
│
├── /drm                          # Deployment Readiness Mapper (v1 — July 2026)
│   ├── README.md                 # DRM architecture and usage
│   ├── /backend                  # FastAPI + Pydantic v2 pipeline
│   │   ├── decomposer.py         # Stage 1: workflow decomposition agent
│   │   ├── analyst.py            # Stage 2: per-stage analysis agent
│   │   ├── synthesizer.py        # Stage 3: report synthesis agent
│   │   └── main.py               # FastAPI entry point
│   ├── /frontend                 # React / TypeScript UI
│   └── /schemas                  # Pydantic output models
│
├── /signals                      # Robothropic Signal — rapid demos
│   └── /[signal-slug]/           # One folder per Signal post
│       ├── README.md             # What this demonstrates + Substack link
│       └── demo.py               # Self-contained script or notebook
│
└── /notebooks                    # Jupyter notebooks for analytical pieces
```

---

## Current Build: Deployment Readiness Mapper (DRM)

**Status**: In development — release target July 1–5, 2026

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
[ Decomposer Agent ]  →  parse stages, actors, data flows, dependencies
        │
        ▼
[ Analyst Agent ]     →  score each stage across all three dimensions (parallelisable)
        │
        ▼
[ Synthesizer Agent ] →  executive summary + per-stage breakdown + priority map
        │
        ▼
Output: structured JSON + human-readable Markdown report
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Claude API (`claude-sonnet-4`) |
| Backend | FastAPI + Pydantic v2 |
| Frontend | React + TypeScript |
| Output | Structured JSON + Markdown |
| License | Apache 2.0 |

The DRM is the first module. Subsequent modules extend the toolkit as the platform grows.

---

## Robothropic Signal

Alongside the main builds, this repository hosts rapid demos triggered by notable papers, deployments, or field developments — the engineering complement to the [Robothropic Signal](https://robothropicai.substack.com) posts.

Each Signal demo is:
- Self-contained in its own `/signals/[slug]/` folder
- Runnable with minimal setup
- Linked to the companion Substack article
- Shipped the same day the insight appears

---

## Application Domains

This toolkit is domain-agnostic at the architecture level. Current and planned application domains:

- **Industrial Robotics**: factory floors, advanced manufacturing, logistics, process automation
- **Space Operations**: planetary exploration, on-orbit systems, autonomous navigation
- **Advanced Manufacturing**: quality inspection, assembly, process control
- **Physical AI Infrastructure**: deployment readiness, integration surface analysis, agent observability

---

## Tech Foundation

All builds in this toolkit share a common stack:

- **LLM backbone**: [Anthropic Claude API](https://www.anthropic.com)
- **Backend**: FastAPI + Pydantic v2
- **Frontend**: React + TypeScript
- **Output formats**: structured JSON, Markdown, future: interactive dashboard
- **License**: Apache 2.0

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
