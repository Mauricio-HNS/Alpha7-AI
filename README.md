# Zero-Agent

## From AI Models to Autonomous Software Agents

Zero-Agent is an experimental AI agent platform built from scratch in Python, without agent frameworks. Its goal is to transform language models into systems that can progressively understand goals, use tools, retrieve knowledge, plan tasks, execute actions, evaluate results, reflect on failures, correct themselves within a bounded loop, and eventually learn from explicitly approved experiences.

### Core principle

The model provides cognitive capability. Zero-Agent provides the controlled system around it.

```text
User Goal
   ↓
Policy / Rules
   ↓
Memory + RAG
   ↓
Planning
   ↓
Decision
   ↓
Tool Execution
   ↓
Evaluation
   ↓
Reflection / Judge
   ↓
Correction
   └──────────────→ bounded retry
   ↓
Approved Experience
   ↓
Training Dataset
   ↓
Optional LoRA / QLoRA
   ↓
Benchmark
   ↓
Promote model only if it improves
```

Memory and RAG are treated as DATA, NOT INSTRUCTIONS. Retrieved content cannot redefine the agent's policy.

## Architecture evolution

```text
v0.1  Agent                         [DONE]
v0.2  Experience Memory             [DONE]
v0.3  Semantic Memory / BGE-M3      [DONE]
v0.4  RAG                           [DONE]
v0.5  Planning                      [DONE]
v0.6  Evaluation / Reflection       [DONE]
v0.7  Autonomous Loops              [NEXT]
v0.8  Multi-Agent                   [TODO]
v0.9  Multimodal                    [TODO]
v1.0  Stable Agent Architecture     [TODO]
v1.x  Local Model Experiments       [TODO]
v2.x  Fine-tuning                   [TODO]
v3.x  PyTorch Experiments           [TODO]
v4.x  Training Experiments          [TODO]
v5.x  Custom Architectures          [TODO]
```

The roadmap is incremental. A stage is marked DONE only after code, tests, documentation, and validation exist.

## Current implementation

### v0.5 — Planning

Implemented:

- `IPlanner`, `Plan`, `PlanStep`, and `LLMPlanner` in `app/planner.py`;
- validated JSON plans using Pydantic;
- sequential step IDs and a maximum number of steps;
- plans explicitly labeled DATA, NOT INSTRUCTIONS;
- optional planner integration in `Agent`;
- `IExecutor` and `ToolExecutor` in `app/executor.py`;
- plan execution remains a separate capability so planning cannot silently execute actions.

### v0.6 — Evaluation / Reflection

Implemented and tested:

- `ReflectionEngine` and `ReflectionResult` in `app/reflection.py`;
- local LLM judge with strict JSON output;
- deterministic evaluator remains the baseline signal;
- invalid judge output fails closed and cannot trigger another action;
- approval-required tools cannot be retried automatically;
- `Agent.run()` now performs a bounded reflect/correct cycle;
- retry count is controlled by `BehavioralPolicy.max_iterations` and `POLICY_MAX_ITERATIONS`;
- `tests/test_reflection.py` covers valid judgement, malformed output, and approval protection;
- `tests/test_autonomous.py` covers successful first attempts, correction retries, and iteration limits;
- `app/autonomous.py` provides the reusable `AutonomousRunner` abstraction for the next autonomy stage.

The current execution cycle is:

```text
Task
 ↓
Agent decision
 ↓
Tool / response
 ↓
Deterministic evaluation
 ↓
Reflection / Judge
 ↓
Success? ── yes ──→ Result
   │
   no
   ↓
Concrete correction
   ↓
Bounded retry
```

The loop does NOT modify model weights. Model learning remains a separate, explicit training pipeline.

## Behavioral policy

`app/policy.py` defines user-owned behavioral constraints.

The policy can define:

- mission;
- mandatory rules;
- prohibited rules;
- tools that require explicit approval;
- maximum autonomous iterations;
- whether learning is restricted to successful experiences.

The important separation is:

```text
SYSTEM / USER POLICY = RULES
MEMORY / RAG          = DATA
MODEL OUTPUT          = PROPOSAL
TOOLS                 = CAPABILITIES
JUDGE                 = EVALUATION
TRAINING              = EXPLICIT LEARNING
```

A retrieved document or previous experience must never become a new behavioral rule merely because the model saw it.

## Learning architecture

`app/learning.py` exports successful, sufficiently important experiences to a training-ready JSONL file.

Example:

```text
data/training/approved.jsonl
```

Only explicitly suitable experiences are exported. The current exporter requires successful experiences with importance >= 0.6 and a non-empty result.

This is intentional. The agent must not silently change its own weights after every interaction.

The planned training pipeline is:

```text
Agent experience
      ↓
Evaluation
      ↓
Human / policy approval
      ↓
approved.jsonl
      ↓
LoRA / QLoRA candidate
      ↓
Benchmark
      ↓
Accept or reject candidate
```

## Local and free-first architecture

The current stack is designed to run locally:

- Ollama for local LLM inference;
- Gemma 3 as the current LLM;
- BGE-M3 for embeddings;
- SQLite for persistent memory;
- Python/Pydantic for the agent architecture;
- no agent framework required.

The long-term training experiments will use optional local dependencies so the lightweight runtime is not forced to install GPU/training packages.

Hardware and electricity are the practical costs of local execution; the software architecture does not require a paid model API.

## What happens when the agent fails

A failure is not automatically treated as a new rule.

```text
Execution
   ↓
Deterministic evaluation
   ↓
Reflection / Judge
   ↓
Concrete correction
   ↓
Bounded retry
   ↓
Final result
```

Only approved successful experiences can later enter the training dataset. This prevents one bad interaction from teaching the model an incorrect behavior.

## Next steps

The next implementation increments should be completed in this order:

1. Strengthen the evaluation rubric while preserving the deterministic evaluator as a baseline.
2. Add an explicit approval workflow for training examples.
3. Add benchmark datasets and model-version tracking.
4. Add an optional local LoRA/QLoRA training script with training dependencies separated from the core runtime.
5. Train a candidate model, benchmark it against the base model, and promote it only when the benchmark improves.
6. Add controlled plan execution so Planner and Executor can cooperate without bypassing policy/approval.
7. Continue to multi-agent and multimodal capabilities only after the core architecture is stable.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start Ollama locally:

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

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama URL |
| `OLLAMA_MODEL` | `gemma3:latest` | Local LLM |
| `EMBEDDING_MODEL` | `bge-m3:latest` | Embedding model |
| `LLM_TIMEOUT` | `60` | LLM timeout in seconds |
| `MAX_STEPS` | `5` | Maximum planner steps |
| `MAX_TOOL_CALLS` | `10` | Reserved tool-call budget |
| `MEMORY_DB_PATH` | `data/memory.db` | SQLite memory database |
| `SEMANTIC_MIN_SCORE` | `0.35` | Semantic retrieval threshold |
| `POLICY_MAX_ITERATIONS` | `5` | Maximum autonomous attempts |

## Existing components

- `ILLM` + `OllamaProvider`;
- Gemma 3 via Ollama;
- `Agent` with decision, tools, evaluation, memory, RAG, planning, policy, reflection, and bounded correction;
- `BehavioralPolicy`;
- `FileSystemTool`;
- `Experience` + `SQLiteMemory`;
- `SimpleEvaluator`;
- `IEmbedder` + `OllamaEmbedder`;
- `Document` + `InMemoryRetriever`;
- `IPlanner` + `LLMPlanner`;
- `IExecutor` + `ToolExecutor`;
- `ReflectionEngine`;
- `AutonomousRunner`;
- approved-experience training exporter;
- structured logging;
- automated tests.

## Project philosophy

Zero-Agent is being built to understand the mechanisms that turn a model into an agent rather than hiding those mechanisms behind a framework.

The final objective is not simply a chatbot that generates text. It is a controlled local system capable of:

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
Improve through measured training
```

The model remains replaceable. The agent architecture remains the controlled layer around it.
