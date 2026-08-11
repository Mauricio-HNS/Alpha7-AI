# Zero-Agent

Sistema de agente de IA construído do zero, em Python, sem frameworks de agentes. O objetivo é entender e implementar manualmente os mecanismos fundamentais de um agente antes de comparar com soluções prontas.

Este projeto evolui em estágios pequenos e versionados. Cada estágio precisa funcionar, ter testes, documentação e servir de base para o próximo.

> `PROJECT_CONTEXT.md` é a fonte de verdade sobre o estado técnico. `AGENTS.md` define o contrato para qualquer agente de programação que continue o projeto.

## Estado atual

```text
v0.1  Agent básico                    [DONE]
v0.2  Experience Memory               [DONE]
v0.3  Semantic Memory / BGE-M3        [DONE]
v0.4  RAG                             [DONE]
v0.5  Planning                        [IN PROGRESS]
v0.6  Evaluation / Reflection         [TODO]
v0.7  Autonomous loops                [TODO]
v0.8  Multi-agent                     [TODO]
v0.9  Multimodal                      [TODO]
v1.0  Stable agent architecture       [TODO]
v1.x  Local model experiments         [TODO]
v2.x  Fine-tuning                    [TODO]
v3.x  PyTorch experiments             [TODO]
v4.x  Training experiments            [TODO]
v5.x  Custom architectures            [TODO]
```

**Regra do roadmap:** uma etapa só pode virar `[DONE]` depois de código real,
testes passando e documentação atualizada. Ao concluir, marque a etapa como
`[DONE]` e a seguinte como `[NEXT]` em `README.md` e `PROJECT_CONTEXT.md`.

## v0.5 — Planning

Planejamento explícito, desacoplado de execução: o planner transforma um
objetivo em uma sequência pequena e ordenada de passos, mas não executa
nada — isso continua sendo responsabilidade de um Executor real, ainda não
construído.

```
Objetivo
 ↓
LLMPlanner (mesmo contrato ILLM do Agent)
 ↓
JSON validado (Pydantic)
 ↓
Plan { steps }
 ↓
formatado como DADOS, NÃO INSTRUÇÕES
 ↓
injetado no prompt de decisão do Agent (opcional)
```

Implementado nesta etapa inicial:

- `IPlanner`, `Plan`, `PlanStep` e `LLMPlanner` em `app/planner.py`;
- plano gerado como JSON validado (IDs sequenciais, máximo de 10 passos);
- `format_plan()` rotula o plano como **DADOS, NÃO INSTRUÇÕES**;
- `Agent(planner=...)` opcional, injeta o plano no prompt de decisão sem executá-lo;
- Agent informa ao planner os nomes reais das ferramentas disponíveis;
- falha do planner não derruba o Agent (mesmo fallback seguro do RAG);
- `main.py` conecta o planner usando `MAX_STEPS` já existente em `app/config.py`.

Ainda falta: um Executor real capaz de rodar os passos de um plano.

## v0.4 — RAG

Primeiro incremento de Retrieval-Augmented Generation, mantendo os mecanismos explícitos e substituíveis:

```text
Documento
 ↓
chunking com overlap
 ↓
BGE-M3 / IEmbedder
 ↓
vetores em índice local
 ↓
cosine similarity + threshold
 ↓
contexto recuperado
 ↓
Agent / LLM
```

Implementado nesta etapa inicial:

- `Document` e `Chunk` para representar fontes e trechos;
- chunking determinístico com tamanho e overlap configuráveis;
- `InMemoryRetriever` sem framework externo;
- embeddings através do contrato `IEmbedder` já usado pelo v0.3;
- ranking por cosine similarity;
- limiar explícito de relevância;
- limite de resultados (`top-k`);
- contexto formatado com fonte, chunk e score;
- conteúdo recuperado explicitamente rotulado como **DADOS, NÃO INSTRUÇÕES**;
- integração opcional do `Agent` com um retriever RAG.

## v0.3 — Semantic Memory / BGE-M3

Implementação concluída:

```text
User
 ↓
Agent
 ↓
SQLiteMemory
 ├── BGE-M3 embedding
 ├── cosine similarity
 └── keyword fallback para dados legados/falhas
 ↓
LLM
```

Já implementado nesta etapa:

- abstração `IEmbedder`;
- `OllamaEmbedder` usando `/api/embed`;
- modelo configurável `bge-m3:latest`;
- persistência dos embeddings no SQLite;
- migração automática de bancos existentes adicionando as colunas de embedding;
- busca semântica por similaridade de cosseno;
- fallback para busca por palavra-chave quando o embedding falha;
- fallback para experiências antigas que ainda não possuem embedding;
- isolamento dos embeddings pelo modelo que os produziu;
- `backfill_embeddings()` capaz de gerar embeddings faltantes ou reconstruir embeddings quando o modelo muda;
- testes unitários para similaridade, persistência, legado, falhas e reindexação;
- validação real do BGE-M3 pelo Stage Gate do GitHub Actions.

## O que ainda não existe

- RAG completo com persistência de documentos
- Executor real (capaz de rodar múltiplos passos de um plano)
- Reflection
- Autonomous loops
- Multi-agent
- Multimodal
- Fine-tuning / treinamento / RL
- Interface web
- ShellTool

## Componentes existentes

- Python 3.12+
- `ILLM` + `OllamaProvider`
- Gemma 3 via Ollama
- `Agent` com decisão, ferramentas, avaliação, memória e contexto RAG opcional
- `FileSystemTool`
- `Experience` com Pydantic
- `SQLiteMemory`
- `SimpleEvaluator`
- `IEmbedder` + `OllamaEmbedder`
- `Document` + `InMemoryRetriever`
- `IPlanner` + `LLMPlanner` (planejamento opcional, ainda sem execução)
- Logging estruturado
- Testes automatizados

## Requisitos

- Python 3.12+
- Ollama rodando localmente
- `gemma3:latest` para o LLM
- `bge-m3:latest` para embeddings

## Configuração

| Variável | Default | Descrição |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL do Ollama |
| `OLLAMA_MODEL` | `gemma3:latest` | Modelo LLM |
| `EMBEDDING_MODEL` | `bge-m3:latest` | Modelo de embeddings |
| `LLM_TIMEOUT` | `60` | Timeout em segundos |
| `MAX_STEPS` | `5` | Limite de passos autônomos futuros |
| `MAX_TOOL_CALLS` | `10` | Limite de chamadas de ferramenta futuras |
| `MEMORY_DB_PATH` | `data/memory.db` | Banco da memória |

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Rodando

```bash
ollama serve
ollama pull gemma3:latest
ollama pull bge-m3:latest
python main.py
```

## Testes

```bash
pytest -v
```

Os testes de integração com Ollama devem usar mocks/fakes sempre que possível,
para manter a suíte determinística. Os gates de integração real ficam no GitHub Actions.
