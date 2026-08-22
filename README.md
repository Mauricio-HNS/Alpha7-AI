# Alpha7 AI

## Autonomous AI, with control

> **Alpha7 — Autonomous Local AI**

> A platform for building, executing, controlling and auditing autonomous AI agents.

**Core promise:** **Autonomy without losing control.**

Alpha7 is a local-first AI agent platform built from scratch in Python, without an agent framework. It progressively combines memory, RAG, planning, controlled tool execution, evaluation, reflection, bounded autonomy and controlled learning.

The project is designed as the foundation of a commercial AI agent platform, not merely as an experiment or framework.

## Technology Battery

![Alpha7 Technology Battery](docs/technology-battery.svg)

**Initial Technology Score: 61 / 100**  
**Technology Maturity Threshold: 70 / 100**

The Technology Battery measures technological capability across Intelligence, Agency, Control and Production. These values are an initial baseline and are not an official technical audit.

[Full Technology Battery methodology](docs/TECHNOLOGY_BATTERY.md)

## Product vision

**AI Agent Control & Orchestration Platform**

Alpha7 is built around a simple principle:

```text
The model proposes.
The system controls.
The user defines the authority.
The platform records what happened.
```

Core lifecycle:

```text
BUILD → DEPLOY → CONTROL → EXECUTE → EVALUATE → AUDIT → IMPROVE
```

See [Product Vision](docs/PRODUCT_VISION.md) and [Branding Strategy](docs/BRANDING.md).

## Core architecture

```text
                         ALPHA7 PLATFORM
                               │
              ┌────────────────┼────────────────┐
              │                │                │
            AGENTS           CONTROL        EVALUATION
              │                │                │
              └────────────────┼────────────────┘
                               │
                          EXECUTION
                               │
                          EXPERIENCE
                               │
                           LEARNING
```

Current agent flow:

```text
USER GOAL
   ↓
POLICY
   ↓
MEMORY + RAG
   ↓
PLANNER
   ↓
VALIDATED PLAN
   ↓
POLICY CHECK
   ↓
EXECUTOR
   ↓
EVALUATION
   ↓
REFLECTION / JUDGE
   ↓
EXPERIENCE
```

Memory, RAG, plans, observations and model output are treated as data, never as authority to override policy.

## Platform layers

### Alpha7 Runtime
- Agent
- Planner
- Plan validation
- Executor
- Tools
- Bounded autonomous execution

### Intelligence Layer
- Local LLM providers
- Memory
- Semantic memory
- RAG
- Knowledge
- Experience

### Control Plane
- Behavioral policies
- Tool permissions
- Approval requirements
- Iteration limits
- Agent configuration

### Evaluation & Trust
- Deterministic evaluation
- LLM Judge
- Reflection
- Auditability
- Replay
- Benchmarks

### Controlled Learning

```text
Experience
 ↓
Evaluation
 ↓
Approved data
 ↓
Training dataset
 ↓
Candidate model
 ↓
Benchmark
 ↓
Promote only if improved
```

Alpha7 must never silently modify model weights after an ordinary interaction.

## Current roadmap

```text
v0.1  Agent                         [DONE]
v0.2  Experience Memory             [DONE]
v0.3  Semantic Memory / BGE-M3      [DONE]
v0.4  RAG                           [DONE]
v0.5  Planning + controlled execute [DONE]
v0.6  Evaluation / Reflection       [DONE]
v0.7  Autonomous Loops              [IN PROGRESS]
v0.8  Multi-Agent                   [TODO]
v0.9  Multimodal                    [TODO]
v1.0  Stable Agent Architecture     [TODO]
v1.x  Local Model Experiments       [TODO]
v2.x  Fine-Tuning                   [TODO]
v3.x  PyTorch Experiments           [TODO]
v4.x  Training Experiments          [TODO]
v5.x  Custom Architectures          [TODO]
```

A milestone becomes DONE only when its code, tests, documentation and automated acceptance gate agree.

## Trust model

1. The user defines the mission and behavioral policy.
2. The model proposes actions; it does not define its own authority.
3. Memory and retrieved knowledge are DATA, not instructions.
4. Planned actions are validated before execution.
5. Configured tools can require explicit approval.
6. Evaluation is separate from execution.
7. Reflection cannot bypass policy.
8. Autonomous retry is bounded.
9. Learning requires approved examples and measurement.
10. The system prefers failing closed to silently exceeding its authority.

## Local-first stack

- Python 3.12
- Ollama
- Gemma 3 for local LLM inference
- BGE-M3 for embeddings
- SQLite for persistent experience memory
- Pydantic for validation
- pytest for automated tests

No paid model API is required by the current architecture.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `gemma3:latest` | Local LLM |
| `EMBEDDING_MODEL` | `bge-m3:latest` | Embedding model |
| `LLM_TIMEOUT` | `60` | LLM timeout |
| `MAX_STEPS` | `5` | Planner step limit |
| `MAX_TOOL_CALLS` | `10` | Reserved tool budget |
| `MEMORY_DB_PATH` | `data/memory.db` | SQLite database |
| `SEMANTIC_MIN_SCORE` | `0.35` | Retrieval threshold |
| `POLICY_MAX_ITERATIONS` | `5` | Autonomous attempt limit |

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start local models:

```bash
ollama serve
ollama pull gemma3:latest
ollama pull bge-m3:latest
```

Run:

```bash
python main.py
```

Tests:

```bash
pytest -v
```

## Project direction

Alpha7 is intended to evolve from a local runtime into a complete agent infrastructure platform:

```text
Alpha7 Core
    ↓
Agent Runtime
    ↓
REST API / SDK
    ↓
CLI
    ↓
Observability
    ↓
Dashboard
    ↓
Enterprise Governance
    ↓
Cloud / Managed Services
```

The core remains local-first and provider-agnostic. Commercial services should be built around stable runtime primitives rather than compromise them.

## Philosophy

The goal is not merely to generate text. The goal is to implement the mechanisms that turn a model into a controlled software agent:

```text
Understand
Plan
Act
Observe
Evaluate
Reflect
Correct
Remember
Learn from approved data
Improve through measurement
```
