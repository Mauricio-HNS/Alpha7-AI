# Zero-Agent

## From AI Model to Controlled Autonomous Agent

> **A platform for building, executing, controlling and auditing autonomous AI agents.**

**Core promise:** **Autonomy without losing control.**

Zero-Agent is the current technical repository and working name for a local-first AI agent platform being built from scratch in Python. The architecture progressively adds memory, RAG, planning, controlled tool execution, evaluation, reflection, bounded autonomy and controlled learning.

The project is being developed as a potential commercial platform, not only as an agent framework or technical experiment.

## Product vision

The intended product category is **AI Agent Control & Orchestration Platform**.

The product is designed around a simple principle:

```text
The model proposes.
The system controls.
The user defines the authority.
The platform records what happened.
```

Core product lifecycle:

```text
BUILD
  ↓
DEPLOY
  ↓
CONTROL
  ↓
EXECUTE
  ↓
EVALUATE
  ↓
AUDIT
  ↓
IMPROVE
```

See [Product Vision](docs/PRODUCT_VISION.md) and [Branding Strategy](docs/BRANDING.md).

## Core architecture

```text
                         PLATFORM
                            │
             ┌──────────────┼──────────────┐
             │              │              │
           AGENTS         CONTROL       EVALUATION
             │              │              │
             └──────────────┼──────────────┘
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

Memory, RAG, plans, tool observations and model output are treated as DATA, not as authority to override policy.

## Commercial product layers

### Agent Runtime

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

### Learning

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

The system must never silently modify model weights after an ordinary interaction.

## Current state

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

A milestone becomes DONE only when its code, tests, documentation and automated acceptance gate all agree.

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

## v0.5 — Planning + controlled execution

Implemented:

- `IPlanner`, `Plan`, `PlanStep` and `LLMPlanner`;
- Pydantic validation of generated plans;
- `IExecutor`, `ToolExecutor` and `StepResult`;
- sequential fail-fast plan execution;
- `Agent(planner=..., executor=...)` integration;
- Policy validation before every planned action;
- explicit approval protection for configured tools;
- `POLICY_MAX_ITERATIONS` wired into the CLI policy;
- integration tests for Planner → Executor → Agent;
- automated stage gate with explicit promotion control.

`Agent.run()` remains one attempt. A planned attempt can contain multiple tool steps, but reflection and retry are not hidden inside the Agent.

## v0.6 — Evaluation + Reflection

The evaluation layer has an explicit single-attempt pipeline:

```text
Agent.run()
   ↓
Deterministic Evaluation
   ↓
ReflectionEngine / LLM Judge
   ↓
EvaluatedRunResult
```

`EvaluationPipeline` connects Agent evaluation with `ReflectionEngine` without adding retry behavior. Bounded retry belongs to v0.7 and is implemented separately by `AutonomousRunner`.

The v0.6 acceptance gate requires the complete test suite plus dedicated Reflection and Evaluation Pipeline tests.

## v0.7 — Autonomous loops

The next implementation milestone introduces bounded autonomous correction and retry while keeping policy enforcement outside the model's authority.

Target flow:

```text
Agent.run()
 ↓
Evaluation
 ↓
Reflection / Judge
 ↓
Correction
 ↓
Policy check
 ↓
Bounded retry
 ↓
Evaluation
```

Partial-failure recovery and re-planning will be introduced explicitly rather than hidden inside the base Agent.

## Stage Gate automation

The acceptance gate is implemented in `scripts/stage_gate.py` and executed by `.github/workflows/stage-gate.yml`.

Automation rules:

- Pull requests validate but cannot promote a milestone.
- Pushes to `main` may promote a milestone automatically.
- Promotion requires `PROMOTE_STAGE=true`.
- The context must contain exactly one `IN PROGRESS` milestone.
- `NEXT MILESTONE` must match the defined milestone order.
- Unsupported milestones are blocked instead of being promoted optimistically.
- Automatic promotion commits use `[skip ci]` to prevent a promotion loop.

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

## Implementation order

1. Complete v0.7 bounded autonomous correction and retry.
2. Add explicit partial-failure and re-planning behavior.
3. Add approval workflow for training examples.
4. Add benchmark datasets and model version tracking.
5. Add optional local LoRA/QLoRA training.
6. Benchmark candidate models against the base model.
7. Promote a trained model only when measured performance improves.
8. Stabilize the runtime before adding commercial API, SDK, dashboard and hosted-platform layers.

## Project philosophy

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
