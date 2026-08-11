<p align="center">
  <img src="ativos/logotipo-agente-zero.svg" alt="Zero-Agent">
</p>

# Zero-Agent

## From AI Models to Autonomous Software Agents

Zero-Agent is an experimental AI agent platform built from scratch in Python, without agent frameworks. Its goal is to transform language models into systems that can progressively understand goals, use tools, retrieve knowledge, plan tasks, execute actions, evaluate results, and move toward autonomous software development.

### The problem

Modern AI models are already capable of generating code, analyzing information, and answering complex questions. A model alone, however, is not a complete autonomous developer.

An autonomous software agent needs architecture around the model to:

- remember previous experiences;
- maintain persistent semantic knowledge;
- retrieve relevant information;
- decompose complex goals into executable steps;
- use tools and interact with real systems;
- verify whether its work actually succeeded;
- detect and correct failures;
- continue working toward a goal without requiring a new human instruction at every step.

Zero-Agent is an exploration of that missing layer.

---

## The idea

The model provides intelligence. Zero-Agent provides the agent architecture around it.

```text
                    AI MODEL
                       │
                       ▼
              ┌─────────────────┐
              │   ZERO-AGENT    │
              ├─────────────────┤
              │ Memory          │
              │ Semantic Memory │
              │ RAG             │
              │ Planning        │
              │ Tools           │
              │ Execution       │
              │ Evaluation      │
              │ Reflection      │
              │ Autonomy        │
              └────────┬────────┘
                       │
                       ▼
                REAL-WORLD ACTION
```

The fundamental transition is:

```text
"Answer my question."

              ↓

"Work toward this goal."
```

---

## From chatbot to agent

A traditional chatbot can be represented as:

```text
User
  │
  ▼
AI Model
  │
  ▼
Response
```

The target architecture of Zero-Agent is:

```text
User
  │
  ▼
Goal
  │
  ▼
Planning
  │
  ▼
Memory + RAG
  │
  ▼
Tool Selection
  │
  ▼
Execution
  │
  ▼
Evaluation
  │
  ▼
Reflection
  │
  ├──── Failure ────► Correction
  │                       │
  │                       ▼
  └────────────────── Execution
                          │
                          ▼
                       Result
```

This is the core idea behind the project: moving from AI that primarily responds to AI systems that can progressively perform work.

---

## Software development as a primary use case

One of the main applications envisioned for Zero-Agent is turning AI models into agents capable of working as software developers.

A future workflow could start with:

```text
GitHub Repository
       +
     Goal
```

For example:

```text
"Add JWT authentication, create the tests,
update the documentation, and prepare a Pull Request."
```

The target workflow is:

```text
Analyze repository
        ↓
Understand architecture
        ↓
Retrieve relevant knowledge
        ↓
Create a plan
        ↓
Modify code
        ↓
Run tests
        ↓
Analyze results
        ↓
Correct problems
        ↓
Run tests again
        ↓
Validate
        ↓
Create Pull Request
```

The goal is not merely to generate code. The goal is to progressively automate the engineering workflow around real software projects.

---

## Architecture evolution

Zero-Agent is intentionally developed in incremental stages. Each stage introduces a fundamental capability and becomes the foundation for the next.

```text
v0.1  Agent
      │
      ▼
v0.2  Experience Memory
      │
      ▼
v0.3  Semantic Memory
      │
      ▼
v0.4  RAG
      │
      ▼
v0.5  Planning
      │
      ▼
v0.6  Evaluation / Reflection
      │
      ▼
v0.7  Autonomous Loops
      │
      ▼
v0.8  Multi-Agent
      │
      ▼
v0.9  Multimodal
      │
      ▼
v1.0  Stable Agent Architecture
```

After the stable agent architecture, the project moves toward model experimentation:

```text
v1.x  Local Models
      │
      ▼
v2.x  Fine-tuning
      │
      ▼
v3.x  PyTorch Experiments
      │
      ▼
v4.x  Training Experiments
      │
      ▼
v5.x  Custom Architectures
```

The first phase builds the agent. The later phases explore the models and architectures that can power it.

---

## Model-agnostic direction

Zero-Agent is designed around abstractions so that the agent architecture does not have to depend permanently on a single model provider.

```text
              ZERO-AGENT
                   │
                   ▼
              LLM / API
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
     Local       Cloud       Future
     Models      Models      Models
```

The current implementation uses Ollama, Gemma 3, and BGE-M3 to enable local development and controlled experimentation.

The architecture is intended to allow different models to occupy the same role as the project evolves.

---

## Built to understand the fundamentals

Zero-Agent deliberately avoids agent frameworks during its core development. The project implements and exposes fundamental mechanisms instead of hiding them behind a high-level framework.

The areas being explored include:

```text
LLM
Memory
Embeddings
Retrieval
RAG
Planning
Execution
Evaluation
Reflection
Autonomy
Multi-Agent
```

This makes Zero-Agent both an agent platform experiment and a research-oriented environment for understanding how agentic systems work internally.

---

## Long-term vision

The project is not intended to become simply another chatbot.

It is also not primarily an attempt to compete with large AI laboratories by training the largest possible language model.

The long-term focus is the layer between an AI model and real-world work:

```text
                AI MODEL
                   │
                   ▼
             ZERO-AGENT
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
    Software     Research    Automation
   Development    Tasks       Tasks
       │           │           │
       └───────────┼───────────┘
                   ▼
              REAL ACTION
```

The vision is to make different AI models usable as specialized agents capable of working toward real goals.

---

## A simple mental model

If an AI model is the brain:

```text
AI MODEL
   =
cognitive capability
```

then Zero-Agent provides the surrounding agent system:

```text
ZERO-AGENT
   =
memory
+ planning
+ tools
+ execution
+ evaluation
+ reflection
+ autonomy
```

Together:

```text
AI Model
    +
Agent Architecture
    =
Autonomous AI Agent
```

---

## Built to evolve

The project is intentionally incremental.

A stage is only considered complete when it has:

```text
Real code
   +
Passing tests
   +
Documentation
   +
Validation
```

This allows every stage to be verified independently and used as a foundation for the next one.

Zero-Agent is not being built as a single AI demonstration. It is being developed as an experimental architecture that can evolve from a basic agent toward autonomous agents and, later, toward experimentation with models, training, and custom architectures.

---

## Current status

```text
v0.1  Basic Agent                     [DONE]
v0.2  Experience Memory               [DONE]
v0.3  Semantic Memory / BGE-M3        [DONE]
v0.4  RAG                             [DONE]
v0.5  Planning                        [IN PROGRESS]
v0.6  Evaluation / Reflection         [TODO]
v0.7  Autonomous Loops                [TODO]
v0.8  Multi-Agent                     [TODO]
v0.9  Multimodal                      [TODO]
v1.0  Stable Agent Architecture       [TODO]
v1.x  Local Model Experiments         [TODO]
v2.x  Fine-tuning                     [TODO]
v3.x  PyTorch Experiments             [TODO]
v4.x  Training Experiments            [TODO]
v5.x  Custom Architectures            [TODO]
```

**Roadmap rule:** a stage can only become `[DONE]` after real code, passing tests, and updated documentation. When a stage is completed, mark it `[DONE]` and the next stage `[NEXT]` in `README.md` and `PROJECT_CONTEXT.md`.

---

## v0.5 — Planning

Explicit planning, decoupled from execution: the planner transforms a goal into a small, ordered sequence of steps, but does not execute anything itself — execution remains the responsibility of a real Executor.

```text
Goal
 ↓
LLMPlanner (same ILLM contract as Agent)
 ↓
Validated JSON (Pydantic)
 ↓
Plan { steps }
 ↓
formatted as DATA, NOT INSTRUCTIONS
 ↓
injected into the Agent decision prompt (optional)
```

Implemented in this initial stage:

- `IPlanner`, `Plan`, `PlanStep`, and `LLMPlanner` in `app/planner.py`;
- plans generated as validated JSON (sequential IDs, maximum of 10 steps);
- `format_plan()` labels the plan as **DATA, NOT INSTRUCTIONS**;
- optional `Agent(planner=...)`, injecting the plan into the decision prompt without executing it;
- Agent provides the planner with the real names of available tools;
- planner failure does not crash the Agent (same safe fallback pattern used by RAG);
- `main.py` connects the planner using the existing `MAX_STEPS` from `app/config.py`;
- `IExecutor` + `ToolExecutor` in `app/executor.py`: execute one step or an entire plan against the Agent tools, stopping at the first failed step (fail-fast).

Still missing: connect the Executor to `Agent` so a complete plan can run automatically — Planner and Executor currently exist and are tested, but remain decoupled.

---

## v0.4 — RAG

First Retrieval-Augmented Generation increment, keeping the mechanisms explicit and replaceable:

```text
Document
 ↓
chunking with overlap
 ↓
BGE-M3 / IEmbedder
 ↓
vectors in local index
 ↓
cosine similarity + threshold
 ↓
retrieved context
 ↓
Agent / LLM
```

Implemented in this initial stage:

- `Document` and `Chunk` for representing sources and passages;
- deterministic chunking with configurable size and overlap;
- `InMemoryRetriever` without an external framework;
- embeddings through the `IEmbedder` contract already used by v0.3;
- ranking by cosine similarity;
- explicit relevance threshold;
- result limit (`top-k`);
- context formatted with source, chunk, and score;
- retrieved content explicitly labeled **DATA, NOT INSTRUCTIONS**;
- optional RAG integration with the `Agent`.

## v0.3 — Semantic Memory / BGE-M3

Implementation completed:

```text
User
 ↓
Agent
 ↓
SQLiteMemory
 ├── BGE-M3 embedding
 ├── cosine similarity
 └── keyword fallback for legacy data/failures
 ↓
LLM
```

Implemented in this stage:

- `IEmbedder` abstraction;
- `OllamaEmbedder` using `/api/embed`;
- configurable `bge-m3:latest` model;
- embedding persistence in SQLite;
- automatic migration of existing databases by adding embedding columns;
- semantic search using cosine similarity;
- keyword-search fallback when embeddings fail;
- fallback for old experiences that do not yet have embeddings;
- embedding isolation by the model that produced them;
- `backfill_embeddings()` to generate missing embeddings or rebuild embeddings when the model changes;
- unit tests for similarity, persistence, legacy data, failures, and reindexing;
- real BGE-M3 validation through the GitHub Actions Stage Gate.

## What does not exist yet

- Complete RAG with document persistence
- Automatic execution of a complete plan inside `Agent.run()`
- Reflection
- Autonomous loops
- Multi-agent
- Multimodal
- Fine-tuning / training / RL
- Web interface
- ShellTool

## Existing components

- Python 3.12+
- `ILLM` + `OllamaProvider`
- Gemma 3 via Ollama
- `Agent` with decision, tools, evaluation, memory, and optional RAG context
- `FileSystemTool`
- `Experience` with Pydantic
- `SQLiteMemory`
- `SimpleEvaluator`
- `IEmbedder` + `OllamaEmbedder`
- `Document` + `InMemoryRetriever`
- `IPlanner` + `LLMPlanner` (optional planning, not yet automatically executed)
- `IExecutor` + `ToolExecutor` (executes plan steps, still decoupled from Agent)
- Structured logging
- Automated tests

## Requirements

- Python 3.12+
- Ollama running locally
- `gemma3:latest` for the LLM
- `bge-m3:latest` for embeddings

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama URL |
| `OLLAMA_MODEL` | `gemma3:latest` | LLM model |
| `EMBEDDING_MODEL` | `bge-m3:latest` | Embedding model |
| `LLM_TIMEOUT` | `60` | Timeout in seconds |
| `MAX_STEPS` | `5` | Future autonomous step limit |
| `MAX_TOOL_CALLS` | `10` | Future tool-call limit |
| `MEMORY_DB_PATH` | `data/memory.db` | Memory database |

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

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

Integration tests with Ollama should use mocks/fakes whenever possible to keep the suite deterministic. Real integration gates run in GitHub Actions.
