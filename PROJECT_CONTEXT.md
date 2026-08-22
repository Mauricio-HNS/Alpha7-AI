# PROJECT_CONTEXT.md — Zero-Agent

> Fonte de verdade do estado real do projeto. Este arquivo deve refletir o código e os gates automatizados, não intenções futuras.

## Estado atual

```text
v0.1: DONE
v0.2: DONE
v0.3: DONE
v0.4: DONE
v0.5: DONE
NEXT MILESTONE: v0.6
```

O v0.5 foi reaberto porque a promoção anterior ocorreu antes de o gate verificar a integração real entre Planner, Executor, Agent e Policy. O código agora contém essa integração, mas a etapa só será marcada como DONE depois que o novo gate automatizado passar.

## Arquitetura atual

```text
User Goal
   ↓
Policy
   ↓
Memory + RAG
   ↓
Planner
   ↓
Validated Plan
   ↓
Policy check for every step
   ↓
Executor
   ↓
Evaluation
   ↓
Experience
```

`Agent.run()` executa uma única tentativa. Quando Planner + Executor estão configurados, uma tentativa pode executar um plano completo. Reflection e retries continuam fora do Agent e serão responsabilidade do fluxo autônomo posterior.

## Componentes

| Componente | Status | Observação |
|---|---|---|
| Ollama / ILLM | IMPLEMENTED | inferência local |
| Agent | IMPLEMENTED | contexto, planejamento, execução e avaliação |
| FileSystemTool | IMPLEMENTED | ferramenta local |
| SQLiteMemory | IMPLEMENTED | experiências persistentes |
| Semantic Memory / BGE-M3 | DONE | embeddings + busca semântica |
| RAG | IMPLEMENTED | retrieval vetorial em memória |
| Planner | IMPLEMENTED | plano JSON validado com Pydantic |
| Executor | IMPLEMENTED | execução sequencial fail-fast |
| Planner → Executor → Agent | IMPLEMENTED | integração controlada |
| Policy por ação planejada | IMPLEMENTED | aprovação verificada antes da execução |
| Stage Gate | IMPLEMENTED | validação separada de promoção |
| ReflectionEngine | SCAFFOLDED | não é executado pelo Agent base |
| AutonomousRunner | SCAFFOLDED | bounded loop separado |
| Approved learning dataset | IMPLEMENTED | exportação controlada |
| Fine-tuning / LoRA / QLoRA | TODO | somente após benchmark |

## v0.5 — Planning

### Objetivo

O Planner transforma o objetivo em um plano pequeno e validado. O Executor executa os passos reais. O Agent controla o fluxo e a Policy continua sendo a autoridade sobre ações.

### Regras

1. O plano é DATA, não instrução de comportamento.
2. Apenas ações conhecidas pelo Executor podem ser executadas.
3. A Policy é verificada antes de cada ação.
4. Ferramentas que exigem aprovação nunca são executadas automaticamente.
5. O Executor para no primeiro erro; replanejamento ainda não faz parte do v0.5.
6. `Agent.run()` não inicia reflection nem retry.

### Gate de aceitação

O Stage Gate em `scripts/stage_gate.py` exige:

1. `pytest -v` completo;
2. `tests/test_planner.py`;
3. `tests/test_executor.py`;
4. `tests/test_agent_executor_integration.py`;
5. `tests/test_stage_gate.py`.

Apenas depois de todos os testes passarem o gate pode promover automaticamente v0.5 para DONE.

## Automação do Stage Gate

O workflow `.github/workflows/stage-gate.yml` roda em push e pull request.

- Pull request: valida o estágio, mas nunca modifica `PROJECT_CONTEXT.md`.
- Push em `main`: valida e pode promover automaticamente a etapa.
- O script exige exatamente um marcador `IN PROGRESS`.
- `NEXT MILESTONE` precisa corresponder ao próximo estágio da ordem.
- Uma etapa sem gate explícito é bloqueada.
- A promoção só ocorre quando `PROMOTE_STAGE=true`.
- O commit automático de promoção usa `[skip ci]` para evitar ciclo.

Isso separa duas operações que antes estavam acopladas: validar e promover.

## v0.6 — Evaluation / Reflection

O `ReflectionEngine` já existe como componente testável, mas ainda não é o caminho padrão do Agent.

Próximo trabalho:

```text
Agent attempt
   ↓
Deterministic evaluation
   ↓
LLM Judge / Reflection
   ↓
Correction
   ↓
bounded retry
```

A Reflection não deve ser duplicada dentro de `Agent.run()` e `AutonomousRunner`.

## Aprendizado

Memória não altera pesos do modelo.

```text
Experience
   ↓
Evaluation
   ↓
Approved data
   ↓
JSONL
   ↓
LoRA / QLoRA candidate
   ↓
Benchmark against base
   ↓
Promote only if improved
```

Nenhuma atualização de pesos deve ocorrer automaticamente após uma interação comum.

## Roadmap

```text
v0.1  Agent básico                    [DONE]
v0.2  Experience Memory               [DONE]
v0.3  Semantic Memory / BGE-M3        [DONE]
v0.4  RAG                             [DONE]
v0.5  Planning + controlled execution [DONE]
v0.6  Evaluation / Reflection         [IN PROGRESS]
v0.7  Autonomous loops                [TODO]
v0.8  Multi-agent                     [TODO]
v0.9  Multimodal                      [TODO]
v1.0  Stable agent architecture       [TODO]
v1.x  Local model experiments         [TODO]
v2.x  Fine-tuning                     [TODO]
v3.x  PyTorch experiments             [TODO]
v4.x  Training experiments            [TODO]
v5.x  Custom architectures            [TODO]
```

## Regra de progressão

1. Inspecionar código real.
2. Implementar incremento pequeno.
3. Criar ou atualizar testes.
4. Executar a suíte.
5. Validar o gate específico da etapa.
6. Só então permitir promoção automática.
7. Atualizar documentação no mesmo ciclo.

O sistema deve preferir falhar fechado a promover uma etapa por engano.
