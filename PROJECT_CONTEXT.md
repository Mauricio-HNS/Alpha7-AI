# PROJECT_CONTEXT.md — Alpha7 AI

> Fonte de verdade do estado real do projeto. Este arquivo deve refletir o código, os testes e os gates automatizados — não intenções futuras.

## Product direction

```text
Commercial category:
AI Agent Control & Orchestration Platform

Positioning:
A platform for building, executing, controlling and auditing autonomous AI agents.

Core promise:
Autonomy without losing control.

Repository:
Alpha7-AI
```

Detalhes de produto e branding permanecem em `docs/PRODUCT_VISION.md` e `docs/BRANDING.md`.

## Engineering contract

O estado do Alpha7 deve ser determinado por evidência técnica.

```text
CODE → TEST → FIX → RETEST → AUDIT → DOCUMENT → GATE → APPROVE
```

Nenhuma capacidade ou milestone deve ser promovido apenas porque existe no roadmap ou porque uma interface foi criada.

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

O estado acima deve ser alterado somente após validação do código, testes e Stage Gate.

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

`Agent.run()` executa uma tentativa. `EvaluationPipeline` conecta a tentativa à avaliação/reflection. `AutonomousRunner` é responsável pelo loop bounded do v0.7.

## Componentes auditados

| Componente | Estado | Regra |
|---|---|---|
| Ollama / ILLM | IMPLEMENTED | deve permanecer validado por testes |
| Agent | IMPLEMENTED | contexto, planejamento, execução e avaliação |
| FileSystemTool | IMPLEMENTED | ferramenta local |
| SQLiteMemory | IMPLEMENTED | experiências persistentes |
| Semantic Memory / BGE-M3 | DONE | embeddings + busca semântica |
| RAG | IMPLEMENTED | retrieval vetorial |
| Planner | IMPLEMENTED | plano JSON validado com Pydantic |
| Executor | IMPLEMENTED | execução sequencial fail-fast |
| Planner → Executor → Agent | IMPLEMENTED | integração controlada |
| Policy por ação planejada | IMPLEMENTED | aprovação antes da execução |
| Stage Gate | IMPLEMENTED | validação separada de promoção |
| ReflectionEngine | IMPLEMENTED | judge de uma tentativa, fail-closed |
| EvaluationPipeline | IMPLEMENTED | Agent attempt → Evaluation → Reflection |
| AutonomousRunner | SCAFFOLDED | evolução atual do v0.7 |
| Approved learning dataset | IMPLEMENTED | exportação controlada |
| Fine-tuning / LoRA / QLoRA | TODO | somente após benchmark |

> Os estados acima são auditáveis e devem ser rebaixados se a implementação real deixar de corresponder à descrição.

## v0.7 — Autonomous loops

### Objetivo

Adicionar correção e retry autônomos com limites explícitos, sem permitir que o modelo ultrapasse a autoridade definida pela Policy.

### Regras

1. Retry sempre possui limite explícito.
2. Correction é uma proposta, não autoridade.
3. Cada nova ação passa novamente pela Policy.
4. Ferramentas que exigem aprovação não podem ser chamadas automaticamente.
5. Falhas parciais são observáveis.
6. Re-planning é explícito e validado.
7. O loop não usa recursão ilimitada.
8. O resultado preserva avaliação e histórico das tentativas.
9. Cada tentativa é testável individualmente.
10. Falha de segurança ou autoridade interrompe o loop.

## Definition of Done

Para qualquer incremento funcional:

```text
1. INSPECT
2. PLAN
3. IMPLEMENT
4. TEST
5. FIX
6. RETEST
7. AUDIT
8. DOCUMENT
9. UPDATE BATTERY
10. STAGE GATE
11. COMMIT
12. APPROVE
```

Uma etapa não é `DONE` se qualquer item obrigatório falhar.

## Technology Battery

A Technology Battery mede o estado técnico real do Alpha7 em quatro dimensões:

```text
INTELLIGENCE
AGENCY
CONTROL
PRODUCTION
```

Também acompanha:

```text
Technology Score
Maturity Threshold
Capability Coverage
```

Scores são derivados de evidências reais. Uma feature planejada não aumenta o score. Uma regressão pode reduzir o score.

A Battery deve ser revisada depois de alterações relevantes e nunca pode ficar deliberadamente desatualizada em relação ao código.

## Stage Gate e automação

Os workflows em `.github/workflows/` validam testes e estágio.

- Pull request deve validar sem promover silenciosamente o roadmap.
- Push em `main` pode promover somente quando todos os critérios configurados forem satisfeitos.
- Deve existir exatamente um milestone `IN PROGRESS` quando essa regra estiver habilitada.
- `NEXT MILESTONE` deve corresponder à ordem definida.
- Etapa sem gate explícito é bloqueada.
- Promoção automática exige os critérios configurados pelo workflow.

## Test policy

Toda alteração funcional deve passar, conforme aplicabilidade, por:

```text
Unit
 ↓
Integration
 ↓
End-to-end
 ↓
Full suite
 ↓
Stage Gate
```

Falhou:

```text
FAIL
 ↓
FIX
 ↓
TEST AGAIN
 ↓
ONLY THEN APPROVE
```

Não existe estado aceitável de "funciona, mas os testes estão quebrados".

## Documentation synchronization

Quando o comportamento real mudar, atualizar no mesmo ciclo:

- `PROJECT_CONTEXT.md`
- `README.md` quando aplicável
- documentação técnica relevante
- Technology Battery

Código e documentação devem terminar cada incremento descrevendo o mesmo sistema.

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

1. Auditar o estado real.
2. Escolher a lacuna técnica de maior impacto dentro do milestone atual.
3. Implementar incremento pequeno e controlado.
4. Adicionar/atualizar testes.
5. Rodar a suíte relevante e, quando possível, a suíte completa.
6. Corrigir todas as falhas encontradas.
7. Rodar novamente após as correções.
8. Verificar regressões, segurança e comportamento real.
9. Atualizar documentação.
10. Recalcular a Technology Battery e Capability Coverage.
11. Validar Stage Gate.
12. Só então considerar o incremento aprovado.

Se a auditoria encontrar uma implementação incorreta ou incompleta, corrigir primeiro; novas funcionalidades ficam atrás da correção da base.

O sistema deve preferir **falhar fechado** a promover uma etapa incorretamente ou permitir que um agente ultrapasse sua autoridade.
