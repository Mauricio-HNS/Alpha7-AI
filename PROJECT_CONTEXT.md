# PROJECT_CONTEXT.md — Zero-Agent

> Fonte de verdade do estado real do projeto. Este arquivo deve refletir o código e os gates automatizados, não intenções futuras.

## Product direction

```text
Commercial category:
AI Agent Control & Orchestration Platform

Positioning:
A platform for building, executing, controlling and auditing autonomous AI agents.

Core promise:
Autonomy without losing control.

Commercial name:
NOT YET SELECTED
```

`Zero-Agent` remains the repository and working name until a commercial brand is researched and selected. The final name must be checked for company, product, GitHub, domain and trademark conflicts before adoption.

Detailed product and branding decisions are documented in:

- `docs/PRODUCT_VISION.md`
- `docs/BRANDING.md`

## Estado atual

```text
v0.1: DONE
v0.2: DONE
v0.3: DONE
v0.4: DONE
v0.5: DONE
v0.6: DONE
v0.7: IN PROGRESS
NEXT MILESTONE: v0.8
```

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
Deterministic Evaluation
   ↓
Reflection / Judge
   ↓
Experience
```

`Agent.run()` executa uma única tentativa. Quando Planner + Executor estão configurados, uma tentativa pode executar um plano completo. `EvaluationPipeline` conecta essa tentativa à Reflection sem iniciar retry. `AutonomousRunner` é separado e pertence ao v0.7.

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
| ReflectionEngine | IMPLEMENTED | judge de uma tentativa, fail-closed |
| EvaluationPipeline | IMPLEMENTED | Agent attempt → Evaluation → Reflection |
| AutonomousRunner | SCAFFOLDED | bounded retry separado para v0.7 |
| Approved learning dataset | IMPLEMENTED | exportação controlada |
| Fine-tuning / LoRA / QLoRA | TODO | somente após benchmark |

## v0.6 — Evaluation / Reflection

### Objetivo

Adicionar uma avaliação explícita após cada tentativa do Agent, combinando a avaliação determinística existente com um LLM Judge. O resultado deve ser estruturado, validado e seguro para consumo posterior pelo fluxo autônomo.

### Fluxo implementado

```text
Agent.run()
   ↓
Deterministic Evaluation
   ↓
ReflectionEngine
   ↓
EvaluatedRunResult
```

`EvaluationPipeline` executa exatamente uma tentativa e nunca faz retry. Se o judge solicitar correção, o pipeline apenas devolve essa decisão. O retry fica reservado ao `AutonomousRunner` do v0.7.

## v0.7 — Autonomous loops

### Objetivo

Adicionar correção e retry autônomos com limites explícitos, sem permitir que o modelo ultrapasse a autoridade definida pela Policy.

### Fluxo alvo

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

### Regras

1. Retry sempre possui limite explícito.
2. Correction é uma proposta, não uma autoridade.
3. Cada nova ação passa novamente pela Policy.
4. Ferramentas que exigem aprovação não podem ser chamadas automaticamente.
5. Falhas parciais devem ser observáveis.
6. Re-planning deve ser explícito e validado.
7. O loop não pode usar recursão ilimitada.
8. O resultado final deve preservar a avaliação e o histórico da tentativa.

## Stage Gate e automação

O workflow `.github/workflows/stage-gate.yml` roda em push e pull request.

- Pull request: valida o estágio, mas nunca modifica `PROJECT_CONTEXT.md`.
- Push em `main`: valida e pode promover automaticamente a etapa.
- O script exige exatamente um marcador `IN PROGRESS`.
- `NEXT MILESTONE` precisa corresponder ao próximo estágio da ordem.
- Uma etapa sem gate explícito é bloqueada.
- A promoção só ocorre quando `PROMOTE_STAGE=true`.
- O commit automático de promoção usa `[skip ci]` para evitar ciclo.

Isso separa validação de promoção e impede avanço otimista do roadmap.

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
v0.6  Evaluation / Reflection         [DONE]
v0.7  Autonomous loops                [IN PROGRESS]
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
8. Não introduzir SaaS, billing ou multi-tenancy no core antes de estabilizar as primitivas do runtime.

O sistema deve preferir falhar fechado a promover uma etapa por engano ou permitir que um agente ultrapasse sua autoridade.
