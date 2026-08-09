# Zero-Agent

Sistema de agente de IA construído do zero, em Python, sem frameworks de agentes. O objetivo é entender e implementar manualmente os mecanismos fundamentais de um agente antes de comparar com soluções prontas.

Este projeto evolui em estágios pequenos e versionados. Cada estágio precisa funcionar, ter testes, documentação e servir de base para o próximo.

> `PROJECT_CONTEXT.md` é a fonte de verdade sobre o estado técnico. `AGENTS.md` define o contrato para qualquer agente de programação que continue o projeto.

## Estado atual

```text
v0.1  Agent básico                    [DONE]
v0.2  Experience Memory               [DONE]
v0.3  Semantic Memory / BGE-M3        [IN PROGRESS]
v0.4  RAG                             [TODO]
v0.5  Planning                        [TODO]
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

## v0.3 — Semantic Memory / BGE-M3

Implementação em andamento:

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
- testes unitários para similaridade, persistência, legado, falhas e reindexação.

**Ainda falta para fechar o v0.3:** executar a suíte completa em ambiente real,
validar o `bge-m3` via Ollama e, se necessário, corrigir os últimos detalhes de
integração. Só depois disso o v0.3 poderá ser marcado como `[DONE]`.

## O que ainda não existe

- RAG
- Planner real
- Executor real
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
- `Agent` com decisão, ferramentas, avaliação e memória
- `FileSystemTool`
- `Experience` com Pydantic
- `SQLiteMemory`
- `SimpleEvaluator`
- `IEmbedder` + `OllamaEmbedder`
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
para manter a suíte determinística. A validação final do v0.3 também deve
incluir um teste real do endpoint de embeddings em ambiente local.
