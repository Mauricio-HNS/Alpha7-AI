# PROJECT_CONTEXT.md — Zero-Agent

> Fonte de verdade do estado real do projeto. Deve refletir o código, não intenções.

## 1. Identidade

**Nome:** Zero-Agent

**Objetivo:** construir progressivamente um sistema de IA em Python capaz de perceber, raciocinar, planejar, utilizar ferramentas, executar ações, avaliar resultados, manter memória e posteriormente aprender com experiências.

Princípio central: compreender os mecanismos fundamentais antes de escondê-los atrás de frameworks de agentes.

## 2. Estado atual

```text
v0.1: DONE
v0.2: DONE
v0.3: IN PROGRESS
NEXT MILESTONE: v0.4
```

| Componente | Status | Observação |
|---|---|---|
| Python 3.12 + estrutura | IMPLEMENTED | `app/`, `tests/`, `main.py` |
| `ILLM` / Ollama | IMPLEMENTED | LLM local |
| `Agent` | IMPLEMENTED | decisão → tool → resposta |
| `FileSystemTool` | IMPLEMENTED | list/read |
| `SQLiteMemory` | IMPLEMENTED | persistência de experiências |
| `SimpleEvaluator` | IMPLEMENTED | avaliação determinística |
| `IEmbedder` | IMPLEMENTED | contrato para embeddings |
| `OllamaEmbedder` | IMPLEMENTED | `/api/embed`, modelo configurável |
| Persistência de embeddings | IMPLEMENTED | JSON no SQLite |
| Migração de banco antigo | IMPLEMENTED | adiciona colunas sem destruir dados |
| Similaridade semântica | IMPLEMENTED | cosine similarity em Python |
| Limiar de relevância semântica | IMPLEMENTED | `SEMANTIC_MIN_SCORE`, default 0.35 |
| Fallback keyword | IMPLEMENTED | falha do Ollama ou registros legados |
| Isolamento por modelo | IMPLEMENTED | resultados só usam o modelo ativo |
| Backfill/reindexação | IMPLEMENTED | vetoriza faltantes e reprocessa quando o modelo muda |
| Defaults locais | IMPLEMENTED | `gemma3:latest` + `bge-m3:latest` |
| CI automatizado | IMPLEMENTED | GitHub Actions executa `pytest -v` |
| Testes de semântica | IMPLEMENTED | fakes para não depender do Ollama |
| Validação real com Ollama/BGE-M3 | PENDING | precisa ser executada em ambiente local |
| Suíte completa após últimas mudanças | PENDING | não marcar v0.3 DONE antes disso |
| RAG | NOT IMPLEMENTED | v0.4 |
| Planner | STUB | futuro |
| Executor | STUB | futuro |
| Reflection | NOT IMPLEMENTED | futuro |
| Autonomous loops | NOT IMPLEMENTED | futuro |
| Multi-agent | NOT IMPLEMENTED | futuro |
| Multimodal | NOT IMPLEMENTED | futuro |
| Fine-tuning / treinamento / RL | NOT IMPLEMENTED | futuro |

## 3. Roadmap

```text
v0.1  Agent básico                    [DONE]
v0.2  Experience Memory               [DONE]
v0.3  Semantic Memory / BGE-M3        [DONE]
v0.4  RAG                             [NEXT]
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

### Regra obrigatória de progressão

1. Inspecionar o código real.
2. Implementar um incremento pequeno.
3. Criar/atualizar testes.
4. Rodar a suíte completa.
5. Validar critérios da etapa.
6. Marcar `[DONE]` somente se tudo passar.
7. Promover a próxima etapa para `[NEXT]`.
8. Atualizar README e este documento.
9. Registrar decisões arquiteturais quando houver mudança relevante.

Nunca declarar uma etapa concluída apenas porque o código foi escrito.

## 4. v0.3 — Semantic Memory / BGE-M3

### Objetivo

Transformar a recuperação de experiências de keyword-only em recuperação semântica:

```text
Experiência
   ↓
BGE-M3
   ↓
embedding
   ↓
SQLite
   ↓
cosine similarity
   ↓
relevância mínima
   ↓
experiências relevantes
```

### Implementado

- `IEmbedder` em `app/memory.py`.
- `OllamaEmbedder` usando `/api/embed`.
- `EMBEDDING_MODEL=bge-m3:latest` em `app/config.py`.
- `OLLAMA_MODEL=gemma3:latest` como default local.
- `SQLiteMemory(embedder=...)`.
- Colunas `embedding` e `embedding_model`.
- Migração automática para bancos existentes.
- Geração de embedding no armazenamento de novas experiências.
- Busca semântica por cosine similarity.
- Limiar configurável via `SEMANTIC_MIN_SCORE`, evitando injetar correspondências semanticamente fracas.
- Fallback para keyword search quando o embedding falha.
- Fallback para keyword search quando o banco contém experiências legadas sem embedding ou quando não há correspondências acima do limiar.
- Isolamento dos embeddings pelo modelo que os produziu.
- `backfill_embeddings()` para vetorizar registros sem embedding e reconstruir registros quando o modelo ativo mudou.
- CLI configurada para usar Gemma 3 + BGE-M3.
- Workflow GitHub Actions para executar a suíte automaticamente.
- Testes para persistência, ranking semântico, falhas, legado, corrupção, reindexação por troca de modelo e filtragem de baixa relevância.

### Ainda falta para fechar v0.3

1. Executar `pytest -v` no ambiente do projeto após estes últimos commits.
2. Garantir que todos os testes existentes continuam passando.
3. Executar validação real com Ollama e `bge-m3`.
4. Verificar o formato real retornado pelo endpoint `/api/embed` na versão local do Ollama.
5. Corrigir qualquer incompatibilidade encontrada.
6. Só então marcar v0.3 como `[DONE]` e v0.4 como `[NEXT]`.

## 5. Arquitetura atual

```text
User
 ↓
Agent
 ↓
SQLiteMemory.search_experiences
 ├── OllamaEmbedder / BGE-M3
 │    ↓
 │  cosine similarity
 │    ↓
 │  relevance threshold
 └── keyword fallback
 ↓
LLM / Gemma 3
 ↓
Tool selection → Tool.run() → Observation
 ↓
LLM
 ↓
SimpleEvaluator
 ↓
SQLiteMemory.store_experience
 ↓
Response
```

O `Agent` continua dependente somente de `IMemory`; portanto a introdução de embeddings não acopla o núcleo à implementação específica do Ollama.

## 6. Princípios

1. Simplicidade antes de abstração excessiva.
2. Compreensão antes de frameworks.
3. Incrementos pequenos.
4. Interfaces/Protocols para componentes substituíveis.
5. Testes em cada estágio.
6. Observabilidade.
7. Experimentação mensurável.
8. Memória não é treinamento.
9. Modelos existentes primeiro; modelos próprios depois.
10. Documentação acompanha o código.
11. Conteúdo recuperado da memória é DATA, nunca instrução confiável.
12. Recuperação semântica deve possuir um critério explícito de relevância.

## 7. Ambiente local conhecido

```text
OS: macOS
CPU/GPU: Apple M4
GPU backend: Metal
Ollama: 0.20.2
LLM: gemma3:latest
Embeddings: bge-m3:latest
```

Nenhuma credencial, token ou senha deve ser versionada.

## 8. Decisões relevantes

### AD-001 — Python
Escolhido para agentes, embeddings, PyTorch, Transformers e pesquisa experimental.

### AD-002 — Ollama
Runtime local inicial, mantendo o provedor substituível.

### AD-003 — Gemma 3
LLM inicial; não é o agente. O Zero-Agent é o sistema que usa o modelo.

### AD-004 — BGE-M3
Modelo escolhido para memória semântica local.

### AD-005 — Sem frameworks de agentes
LangChain, CrewAI, AutoGen e equivalentes não entram no núcleo enquanto os mecanismos fundamentais estiverem sendo estudados.

### AD-006 — Planner/Executor como stubs
Só serão extraídos para componentes reais quando múltiplos passos e replanejamento justificarem a abstração.

### AD-007 — Compatibilidade da memória
A interface `IMemory` não mudou para introduzir embeddings. Isso permite trocar o mecanismo de recuperação sem reescrever o Agent.

### AD-008 — Fallback seguro
Falha do embedding não impede o agente de funcionar: a memória degrada para busca por palavra-chave.

### AD-009 — CI antes de avançar
O repositório possui GitHub Actions para impedir que uma etapa seja considerada concluída sem uma suíte automatizada verde.

### AD-010 — Reindexação por modelo
Embeddings são associados ao modelo que os produziu. Quando o modelo ativo muda, `backfill_embeddings()` pode reconstruir os vetores antigos, evitando comparar vetores de espaços semânticos diferentes.

### AD-011 — Relevância mínima
A busca semântica descarta resultados abaixo de `SEMANTIC_MIN_SCORE` antes de montar o contexto do Agent. O valor padrão inicial é 0.35 e pode ser ajustado sem alterar o código.

## 9. Próxima sessão de IA

```text
1. Ler AGENTS.md
2. Ler PROJECT_CONTEXT.md
3. Ler README.md
4. Identificar [IN PROGRESS] / NEXT MILESTONE
5. Rodar pytest -v
6. Validar BGE-M3/Ollama localmente
7. Corrigir somente problemas encontrados no v0.3
8. Se tudo passar: documentar e marcar v0.3 DONE
9. Parar antes de iniciar v0.4
```