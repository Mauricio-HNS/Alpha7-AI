<div align="center">

# Zero-Agent

### From AI Models to Autonomous Software Agents

Experimental agent architecture built from scratch in Python, focused on the engineering layer between an LLM and real-world work.

[Architecture](docs/portfolio/ARCHITECTURE.md) · [Tests](tests) · [Project Context](PROJECT_CONTEXT.md)

</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/LLM-Ollama-111827?style=for-the-badge" alt="LLM" />
  <img src="https://img.shields.io/badge/RAG-BGE--M3-0F766E?style=for-the-badge" alt="RAG" />
  <img src="https://img.shields.io/badge/Architecture-Agentic-4C1D95?style=for-the-badge" alt="Agentic architecture" />
</p>

## What is Zero-Agent?

Zero-Agent explores the architecture required to turn a language model into a system that can work toward goals instead of only producing responses.

The model provides cognitive capability. Zero-Agent provides the surrounding runtime:

```text
AI Model
   +
Memory + RAG + Planning + Tools + Execution + Evaluation
   =
Goal-oriented AI Agent
```

The project deliberately avoids agent frameworks in its core so the mechanisms remain explicit, replaceable and testable.

## Architecture

```text
Goal
  |
  v
Agent
  |
  +----> Memory / Semantic Search
  |
  +----> RAG
  |
  +----> Planner
  |
  v
Executor
  |
  v
Tools
  |
  v
Evaluation
  |
  +---- success ----> Result
  |
  +---- failure ----> Correction -> Execution
```

See the detailed [architecture overview](docs/portfolio/ARCHITECTURE.md).

## Current capabilities

| Capability | Status |
|---|---|
| Basic Agent | Done |
| Experience Memory | Done |
| Semantic Memory / BGE-M3 | Done |
| Retrieval-Augmented Generation | Done |
| Explicit Planning | In progress |
| Plan Execution | Implemented, integration pending |
| Evaluation / Reflection | Next |
| Autonomous Loops | Planned |
| Multi-Agent | Planned |
| Multimodal | Planned |

### v0.5 — Planning

The planner transforms a goal into a bounded, validated sequence of steps without executing those steps itself.

Implemented:

- `IPlanner`, `Plan`, `PlanStep` and `LLMPlanner`;
- validated structured JSON through Pydantic;
- sequential step IDs and a maximum of 10 steps;
- plans explicitly marked as `DATA, NOT INSTRUCTIONS`;
- optional planner integration with `Agent`;
- real tool names supplied to the planner;
- safe planner fallback when planning fails;
- `IExecutor` and `ToolExecutor` for single-step and full-plan execution;
- fail-fast execution when a step fails.

The current boundary is intentional: Planner and Executor are tested independently, while automatic execution from `Agent` remains the next milestone.

## v0.4 — RAG

```text
Document
   |
   v
Chunking
   |
   v
BGE-M3 Embeddings
   |
   v
Vector Retrieval
   |
   v
Relevant Context
   |
   v
Agent / LLM
```

Implemented with explicit, replaceable mechanisms:

- `Document` and `Chunk` models;
- deterministic chunking with overlap;
- `InMemoryRetriever`;
- embedding abstraction through `IEmbedder`;
- cosine-similarity ranking;
- relevance threshold and top-k limits;
- source/chunk/score context formatting;
- retrieved content marked as `DATA, NOT INSTRUCTIONS`;
- optional Agent integration.

## v0.3 — Semantic Memory

Semantic memory uses BGE-M3 embeddings persisted in SQLite, with keyword fallback for legacy data or embedding failures.

Implemented capabilities include embedding isolation by model, database migration for existing records, semantic similarity search, legacy-data fallback and `backfill_embeddings()` for rebuilding indexes.

## Software development as a target use case

One long-term direction is an agent capable of working through real software-engineering workflows:

```text
Repository + Goal
       |
       v
Understand architecture
       |
       v
Retrieve knowledge
       |
       v
Plan changes
       |
       v
Modify code
       |
       v
Run tests
       |
       v
Evaluate
       |
       +---- failure --> correct --> test again
       |
       v
Validate
       |
       v
Prepare Pull Request
```

The objective is workflow automation, not simply code generation.

## Design principles

- Model-agnostic provider boundary.
- Explicit interfaces instead of framework-dependent magic.
- Bounded execution and configurable limits.
- Structured validation between components.
- Retrieved knowledge treated as data, not executable instructions.
- Incremental milestones backed by code, tests and documentation.

## Current stack

- Python 3.12+
- Ollama
- Gemma 3
- BGE-M3
- Pydantic
- SQLite
- pytest

## Requirements

- Python 3.12+
- Ollama running locally
- `gemma3:latest`
- `bge-m3:latest`

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
ollama serve
ollama pull gemma3:latest
ollama pull bge-m3:latest
python main.py
```

## Tests

```bash
pytest -v
```

Integration tests should prefer mocks/fakes for deterministic local execution. Real integration gates run in GitHub Actions.

## Roadmap

```text
v0.5  Planning / execution integration
v0.6  Evaluation + reflection
v0.7  Bounded autonomous loops
v0.8  Multi-agent orchestration
v0.9  Multimodal capabilities
v1.0  Stable agent architecture
v1.x  Local model experimentation
v2.x  Fine-tuning experiments
v3.x  PyTorch experiments
v4.x  Training experiments
v5.x  Custom architectures
```

A milestone is considered complete only when the implementation, tests and documentation support it.
