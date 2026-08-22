# Zero-Agent

## From AI Model to Controlled Autonomous Agent

Zero-Agent is a local-first AI agent architecture built from scratch in Python, without an agent framework. The project progressively adds memory, RAG, planning, tool execution, evaluation, reflection, bounded autonomy and, later, controlled learning.

## Core principle

```text
USER
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

The model proposes. The system controls. Memory and RAG are DATA, not instructions.

## Current state

```text
v0.1  Agent                         [DONE]
v0.2  Experience Memory             [DONE]
v0.3  Semantic Memory / BGE-M3      [DONE]
v0.4  RAG                           [DONE]
v0.5  Planning + controlled execute [DONE]
v0.6  Evaluation / Reflection       [IN PROGRESS]
v0.7  Autonomous Loops              [TODO]
v0.8  Multi-Agent                   [TODO]
v0.9  Multimodal                    [TODO]
v1.0  Stable Agent Architecture     [TODO]
v1.x  Local Model Experiments       [TODO]
v2.x  Fine-Tuning                  [TODO]
```

A milestone becomes DONE only when its code, tests, documentation and automated acceptance gate all agree.

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

The evaluation layer now has an explicit single-attempt pipeline:

```text
Agent.run()
   ↓
Deterministic Evaluation
   ↓
ReflectionEngine / LLM Judge
   ↓
EvaluatedRunResult
```

`EvaluationPipeline` connects the existing Agent evaluation with `ReflectionEngine` without adding retry behavior. This is intentional: bounded retry belongs to v0.7 and is implemented separately by `AutonomousRunner`.

The v0.6 acceptance gate requires the complete test suite plus dedicated Reflection and Evaluation Pipeline tests.

## Execution flow

```text
Goal
 ↓
Memory / RAG
 ↓
Planner
 ↓
Plan validation
 ↓
For every step:
    Policy check
    ↓
    Executor
 ↓
Evaluation
 ↓
Reflection / Judge
 ↓
Experience
```

If a planned tool requires explicit approval, execution stops before the tool is called.

The current Executor is fail-fast. Partial-failure recovery and re-planning belong to later milestones.

## Stage Gate automation

The acceptance gate is implemented in `scripts/stage_gate.py` and executed by `.github/workflows/stage-gate.yml`.

For each active milestone, the gate requires the complete test suite plus milestone-specific acceptance tests. v0.5 validates Planner → Executor → Agent integration. v0.6 validates Reflection and the single-attempt Evaluation Pipeline.

Automation rules:

- Pull requests validate but cannot promote a milestone.
- Pushes to `main` may promote a milestone automatically.
- Promotion requires `PROMOTE_STAGE=true`.
- The context must contain exactly one `IN PROGRESS` milestone.
- `NEXT MILESTONE` must match the defined milestone order.
- Unsupported milestones are blocked instead of being promoted optimistically.
- Automatic promotion commits use `[skip ci]` to prevent a promotion loop.

This prevents the previous failure mode where CI could advance the roadmap before the real implementation was part of the acceptance criteria.

## Reflection and autonomy

Reflection is deliberately outside the base Agent:

```text
Agent.run() — one attempt
 ↓
Evaluation
 ↓
Reflection / Judge
 ↓
Correction
 ↓
Bounded retry
```

`ReflectionEngine` evaluates one attempt. `EvaluationPipeline` connects that evaluation to the Agent without retrying. `AutonomousRunner` remains a separate v0.7 component responsible for bounded correction and retry.

## Learning architecture

Memory is not training.

```text
Experience
 ↓
Evaluation
 ↓
Approved example
 ↓
JSONL dataset
 ↓
LoRA / QLoRA candidate
 ↓
Benchmark against base model
 ↓
Promote only if improved
```

The system must never silently modify model weights after an ordinary interaction.

## Local-first stack

- Python 3.12
- Ollama
- Gemma 3 for local LLM inference
- BGE-M3 for embeddings
- SQLite for persistent experience memory
- Pydantic for validation
- pytest for automated tests

No paid model API is required by the architecture.

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

## Next implementation order

1. Finish and automatically validate v0.6.
2. Integrate bounded autonomous correction and retry as v0.7.
3. Add explicit partial-failure and re-planning behavior.
4. Add approval workflow for training examples.
5. Add benchmark datasets and model version tracking.
6. Add optional local LoRA/QLoRA training.
7. Benchmark candidate models against the base model.
8. Promote a trained model only when measured performance improves.

## Project philosophy

The goal is not merely to generate text. The goal is to understand and implement the mechanisms that turn a model into a controlled software agent:

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
