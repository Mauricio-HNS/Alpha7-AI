# Zero-Agent Architecture

Zero-Agent is organized around a model-independent agent runtime. The model provides reasoning capability; the runtime provides memory, retrieval, planning, tools, execution and validation.

```text
                    User Goal
                        |
                        v
                  +-----------+
                  |   Agent   |
                  +-----+-----+
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
       Memory          RAG          Planner
          |             |             |
          +-------------+-------------+
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
                 +------+------+
                 |             |
              success        failure
                 |             |
                 v             v
               Result      correction
                               |
                               +------> Executor
```

## Current implementation

- `ILLM` and `OllamaProvider` isolate the language model provider.
- `SQLiteMemory` stores experiences and supports semantic retrieval through BGE-M3.
- `Document` and `InMemoryRetriever` provide the initial RAG layer.
- `LLMPlanner` converts a goal into validated, bounded plan data.
- `ToolExecutor` executes individual plan steps while preserving fail-fast behavior.
- `SimpleEvaluator` provides explicit result evaluation.
- Structured logging and automated tests provide observability and regression protection.

## Current boundary

Planning and execution are intentionally separate. The next architectural milestone is connecting the validated plan to the Agent execution loop while preserving safety limits, deterministic validation and testability.

## Design principles

1. Model-agnostic core.
2. Explicit contracts instead of framework magic.
3. Bounded autonomy.
4. Validated structured data between components.
5. Retrieval content treated as data, not instructions.
6. Every capability should be independently testable.
