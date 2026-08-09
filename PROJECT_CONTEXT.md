# PROJECT_CONTEXT.md — Zero-Agent

> Este documento é a fonte de verdade sobre o estado do projeto. Ele deve
> refletir o **código real**, não intenções. Se algo aqui divergir do
> código, o código está certo e este arquivo precisa ser corrigido.

---

## 1. Identidade

**Nome:** Zero-Agent

**Objetivo:** construir progressivamente, começando praticamente do zero,
um sistema de IA em Python capaz de perceber, raciocinar, planejar,
utilizar ferramentas, executar ações, avaliar resultados, manter memória
e, posteriormente, aprender com experiências.

O projeto é também um estudo experimental: até onde é possível chegar
construindo sistemas de IA com recursos limitados (hardware local, sem
frameworks de agentes prontos), entendendo cada mecanismo antes de usar
abstrações de terceiros.

---

## 2. Estado atual

```text
Version: v0.2 (incremento 1 de 2)
Status: em andamento
```

| Componente | Status | Observação |
|---|---|---|
| Python 3.12 + estrutura do projeto | IMPLEMENTED | `app/`, `tests/`, `main.py` |
| Abstração de LLM (`ILLM`) | IMPLEMENTED | `app/llm.py` |
| `OllamaProvider` | IMPLEMENTED | HTTP para `/api/generate`, testado com mocks |
| Gemma 3 | IMPLEMENTED (uso) | Modelo padrão via Ollama, configurável por env var |
| `Agent` (decisão → tool → resposta) | IMPLEMENTED | `app/agent.py` |
| `FileSystemTool` (list/read) | IMPLEMENTED | `app/tools/filesystem.py`, restrito a `root_dir` |
| `ShellTool` | **NOT IMPLEMENTED** | Ainda não existe nenhum arquivo relacionado |
| Testes automatizados | IMPLEMENTED | 24 testes, `pytest`, todos passando |
| `SQLiteMemory` (store/get/search) | IMPLEMENTED | `app/memory.py`, testada isoladamente (`tests/test_memory.py`) |
| Integração `Memory` ↔ `Agent` | **NOT IMPLEMENTED** | `Agent` hoje não importa nem usa `app/memory.py` |
| BGE-M3 / embeddings / busca semântica | **NOT IMPLEMENTED** | Modelo disponível no ambiente, mas não integrado ao código |
| `Planner` (`IPlanner`) | STUB | `app/planner.py`: só interface (Protocol), sem lógica |
| `Executor` (`IExecutor`) | STUB | `app/executor.py`: só interface (Protocol), sem lógica |
| `Evaluator` (`IEvaluator`) | STUB | `app/evaluator.py`: só interface (Protocol), sem lógica |
| Configuração (`app/config.py`) | IMPLEMENTED | Via variáveis de ambiente, Pydantic |
| Logging estruturado | IMPLEMENTED | `app/logging_config.py`, ciclo observável via `logger.info` no `Agent` |
| RAG completo | NOT IMPLEMENTED | Planejado para depois de embeddings |
| Multi-agent | NOT IMPLEMENTED | Planejado para depois de um agente único funcionar bem |
| Fine-tuning / treinamento / RL | NOT IMPLEMENTED | Estágios de longo prazo (v2.x+) |
| Interface web | NOT IMPLEMENTED | CLI apenas (`main.py`) |

**Regra ao atualizar esta tabela:** nunca marcar algo como `IMPLEMENTED`
sem antes ler o código correspondente. Uma interface/Protocol sem lógica
é `STUB`, não `IMPLEMENTED`.

---

## 3. Ambiente local conhecido

```text
OS: macOS
CPU/GPU: Apple M4
GPU backend: Metal
GPU memory reported by Ollama: ~11.8 GiB
Ollama: 0.20.2
```

Modelos locais conhecidos:

```text
gemma3:latest   (LLM principal, usado via Ollama)
bge-m3:latest   (disponível para embeddings - ainda não integrado)
```

Nenhuma credencial, token ou senha deve ser adicionada a este arquivo ou
a qualquer outro arquivo versionado. Configuração sensível vive apenas em
`.env` local (git-ignored) — ver `.env.example` para as chaves esperadas.

---

## 4. Arquitetura

### Atual (v0.1 + v0.2 incremento 1, ainda desconectados)

```text
User
 ↓
Agent
 ↓
LLM (decide: responder direto ou usar ferramenta)
 ↓
FileSystemTool
 ↓
Observation
 ↓
LLM (resposta final)
 ↓
Response
```

```text
SQLiteMemory (isolada, sem uso pelo Agent ainda)
 ├── store_experience(Experience) -> id
 ├── get_experience(id) -> Experience | None
 └── search_experiences(query) -> list[Experience]   # busca por palavra-chave
```

### Planejada (próximos incrementos)

```text
Agent
 ├── LLM
 ├── Planner      (stub hoje)
 ├── Executor     (stub hoje)
 ├── Evaluator    (stub hoje)
 ├── Memory
 │    └── SQLiteMemory
 │         └── (futuro) busca semântica via BGE-M3
 └── Tools
      ├── FileSystemTool
      └── (futuro) ShellTool
```

A diferença chave entre "atual" e "planejada": hoje o `Agent` toma a
decisão de tool-use diretamente (sem `Planner`/`Executor`/`Evaluator`
separados, por serem simples demais para justificar módulos próprios) e
não consulta `Memory`. Isso é proposital, não um esquecimento — ver AD e
princípios abaixo.

---

## 5. Princípios do projeto

1. Simplicidade antes de abstração excessiva.
2. Compreensão antes de frameworks.
3. Implementação incremental — nunca tudo de uma vez.
4. Componentes substituíveis (interfaces/Protocols, não acoplamento direto).
5. Testes em cada estágio.
6. Observabilidade (logs do ciclo cognitivo).
7. Experimentação mensurável (benchmarks, quando existirem).
8. Nenhuma funcionalidade adicionada sem necessidade real.
9. Memória não é treinamento.
10. Usar modelos existentes inicialmente; estudar modelos próprios depois.

---

## 6. Architectural Decisions

### AD-001 — Python

Python foi escolhido porque o objetivo de longo prazo inclui agentes,
modelos locais, embeddings, PyTorch, Transformers, fine-tuning,
treinamento experimental e pesquisa em geral.

### AD-002 — Ollama

Ollama é usado inicialmente para executar modelos localmente, abstraído
por trás de `ILLM` para poder ser substituído sem tocar no núcleo.

### AD-003 — Gemma 3

Gemma 3 é o LLM inicial. É um componente substituível e **não é** o
próprio Zero-Agent — o agente é o sistema em torno do modelo, não o
modelo em si (ver seção "Modelo mental" abaixo).

### AD-004 — BGE-M3

BGE-M3 será usado posteriormente para embeddings/memória semântica. Não
foi integrado prematuramente: o v0.2 (incremento 1) implementou memória
com busca por palavra-chave primeiro, deliberadamente, para não acoplar
a camada de persistência a uma dependência de embeddings antes de
precisar dela.

### AD-005 — Sem frameworks de agentes inicialmente

Não usar LangChain, CrewAI, AutoGen ou similares no núcleo. Objetivo:
compreender e implementar manualmente os mecanismos fundamentais antes de
comparar com soluções prontas.

### AD-006 — Planner/Executor/Evaluator como stubs no v0.1/v0.2

Criados como interfaces (Protocol) desde o v0.1 para que o resto do
sistema já pudesse depender delas por tipo, mas sem lógica: no v0.1 e
v0.2 (incremento 1), a decisão de tool-use é simples o suficiente para
viver dentro do próprio `Agent`. Extrair para módulos dedicados é
trabalho de quando houver de fato múltiplos passos, replanejamento ou
avaliação de qualidade a implementar (v0.5/v0.6 neste roadmap).

### AD-007 — Memory != Agent (ainda)

`SQLiteMemory` foi implementada e testada isoladamente antes de ser
conectada ao `Agent`, de propósito, para poder validar a camada de
persistência (schema, store, get, search) sem misturar bugs de
integração com bugs de lógica de memória. A integração é o próximo
incremento documentado.

---

## 7. Modelo mental

```text
MODEL ≠ RUNTIME ≠ AGENT
```

```text
Gemma 3    = modelo (os pesos, o "cérebro" que gera texto)
Ollama     = runtime (o programa que carrega e serve o modelo localmente)
Zero-Agent = sistema/agente que USA o modelo através do runtime,
             mas que também percebe, planeja, usa ferramentas, observa,
             avalia e (eventualmente) lembra - nada disso é o modelo em si.
```

Trocar Gemma 3 por outro modelo, ou Ollama por outro runtime, não deveria
exigir reescrever o Agent — é exatamente para isso que existe `ILLM`.

---

## 8. Roadmap

```text
v0.1  Agent básico                    [DONE]
v0.2  Memory                          [EM ANDAMENTO - incremento 1/2 concluído]
v0.3  Embeddings / BGE-M3
v0.4  RAG
v0.5  Planning
v0.6  Evaluation / Reflection
v0.7  Autonomous loops
v0.8  Multi-agent
v0.9  Multimodal
v1.0  Stable agent architecture
v1.x  Local model experiments
v2.x  Fine-tuning
v3.x  PyTorch experiments
v4.x  Training experiments
v5.x  Custom architectures
```

Este roadmap não é definitivo. Cada estágio é revisado com base em
resultados experimentais reais, não avançado automaticamente.

---

## 9. Próximo passo

```text
NEXT MILESTONE: v0.2 (incremento 2 de 2)
```

**Objetivo:** Experience-based Memory integrada ao `Agent`.

```text
Task
 ↓
Agent
 ↓
LLM
 ↓
Tool
 ↓
Result
 ↓
Evaluation (básica: success/evaluation/importance)
 ↓
Memory.store_experience
```

E, em uma nova tarefa:

```text
New Task
 ↓
Memory.search_experiences
 ↓
Relevant Experience(s)
 ↓
LLM Context (rotulado explicitamente como "experiências anteriores,
             não instruções")
 ↓
Better-informed Decision
```

Isso é **memory-based learning** (ou *experience-based memory*) — os
parâmetros do Gemma 3 não são alterados. Isso é explicitamente diferente
de fine-tuning ou reinforcement learning, que são estágios futuros
separados no roadmap (v2.x/v4.x).

---

## 10. O que não implementar ainda

```text
Do not implement yet:

- fine-tuning
- model training
- reinforcement learning
- multi-agent
- voice
- vision
- unrestricted autonomy
- web UI
- vector database / embeddings semânticos (BGE-M3 vem depois da
  integração Memory <-> Agent com busca por palavra-chave)
- complex agent frameworks (LangChain, CrewAI, AutoGen, etc.)
- ShellTool (ainda não priorizado; quando implementado, precisa de
  camada de autorização antes de qualquer comando potencialmente
  destrutivo)
```

---

## 11. Continuing the project in a new AI session

O repositório (código + `PROJECT_CONTEXT.md` + `AGENTS.md` + histórico do
Git) é a fonte de verdade. Nenhuma sessão de IA deve depender do
histórico de conversa anterior.

```text
1. Clone/open the repository.
2. Read AGENTS.md.
3. Read PROJECT_CONTEXT.md.
4. Read README.md.
5. Inspect git status.
6. Inspect the latest commits.
7. Verify the current implementation (read the actual code, don't trust
   docs blindly - docs can drift from code).
8. Continue only from the documented NEXT MILESTONE.
```
