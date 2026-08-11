# PROJECT_CONTEXT.md — Zero-Agent

> Fonte de verdade do estado real do projeto. Deve refletir o código e os gates automatizados, não intenções.

## 1. Identidade

**Nome:** Zero-Agent

**Objetivo:** construir progressivamente um sistema de IA em Python capaz de perceber, raciocinar, planejar, utilizar ferramentas, executar ações, avaliar resultados, manter memória e posteriormente aprender com experiências.

Princípio central: compreender os mecanismos fundamentais antes de escondê-los atrás de frameworks de agentes.

## 2. Estado atual

```text
v0.1: DONE
v0.2: DONE
v0.3: DONE
v0.4: DONE
v0.5: IN PROGRESS
NEXT MILESTONE: v0.5
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
| CI automatizado | IMPLEMENTED | GitHub Actions executa a suíte |
| Stage Gate automático | IMPLEMENTED | valida critérios explícitos antes de promover etapa |
| Testes de semântica | IMPLEMENTED | fakes para não depender do Ollama |
| Validação real com Ollama/BGE-M3 | DONE | validada pelo Stage Gate |
| RAG: documentos/chunks | IMPLEMENTED | `Document` + chunking determinístico |
| RAG: recuperação vetorial | IMPLEMENTED | `InMemoryRetriever` + cosine similarity |
| RAG: contexto no Agent | IMPLEMENTED | retriever opcional no núcleo do Agent |
| RAG persistente | TODO | próximo incremento do v0.4 |
| `IPlanner` / `LLMPlanner` | IMPLEMENTED | `app/planner.py`, plano JSON validado com Pydantic |
| `Agent(planner=...)` | IMPLEMENTED | plano injetado no prompt de decisão como DATA, opcional, fail-safe |
| `IExecutor` / `ToolExecutor` | IMPLEMENTED | `app/executor.py`; executa `Plan.steps` contra as ferramentas do Agent, fail-fast |
| Execução automática do plano dentro do `Agent.run()` | TODO | Executor existe e está testado isoladamente, mas ainda não é chamado pelo Agent |
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
v0.4  RAG                             [DONE]
v0.5  Planning                        [IN PROGRESS]
v0.6  Evaluation / Reflection         [TODO]
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
- Limiar configurável via `SEMANTIC_MIN_SCORE`, default 0.35.
- Fallback para keyword search quando o embedding falha.
- Fallback para keyword search quando o banco contém experiências legadas sem embedding ou quando não há correspondências acima do limiar.
- Isolamento dos embeddings pelo modelo que os produziu.
- `backfill_embeddings()` para vetorizar registros sem embedding e reconstruir registros quando o modelo ativo mudou.
- CLI configurada para usar Gemma 3 + BGE-M3.
- Testes para persistência, ranking semântico, falhas, legado, corrupção, reindexação por troca de modelo e filtragem de baixa relevância.
- Stage Gate com suíte completa e validação real do endpoint `/api/embed`.

### Critérios de fechamento

1. `pytest -v` deve terminar sem falhas.
2. Ollama deve iniciar no ambiente de CI.
3. `bge-m3:latest` deve ser carregado.
4. `/api/embed` deve responder com sucesso para BGE-M3.
5. O comportamento do teste semântico deve respeitar `SEMANTIC_MIN_SCORE=0.35`.
6. Só depois de todos os gates passarem o Stage Gate pode promover v0.3 para `[DONE]` e v0.4 para `[NEXT]`.

## 5. v0.4 — RAG

### Objetivo

Adicionar Retrieval-Augmented Generation explícito ao Agent, começando por um índice vetorial local simples antes de introduzir persistência ou frameworks externos:

```text
Documento
   ↓
chunking + overlap
   ↓
IEmbedder / BGE-M3
   ↓
índice vetorial local
   ↓
cosine similarity
   ↓
threshold + top-k
   ↓
contexto recuperado
   ↓
Agent / LLM
```

### Implementado neste incremento

- `Document` e `Chunk` em `app/rag.py`.
- Chunking determinístico com `chunk_size` e `chunk_overlap`.
- `InMemoryRetriever` sem framework de agentes ou banco vetorial externo.
- Reuso do contrato `IEmbedder` do v0.3.
- Ranking por cosine similarity.
- Threshold explícito e `top-k`.
- Contexto formatado com `source`, número do chunk e score.
- Conteúdo recuperado rotulado como **DADOS, NÃO INSTRUÇÕES**.
- `Agent(retriever=...)` opcional, preservando compatibilidade com o Agent existente.
- Falha de recuperação não derruba o Agent: ele continua sem contexto RAG.

### Próximos incrementos do v0.4

- persistência do índice/documentos;
- ingestão de arquivos do projeto;
- deduplicação e atualização de documentos;
- avaliação de qualidade de retrieval;
- gate real de RAG no GitHub Actions.

### Critérios de fechamento

1. `pytest -v` deve terminar sem falhas.
2. Chunking deve preservar fonte, ordem e overlap configurados.
3. Retrieval deve respeitar cosine similarity, threshold e top-k.
4. O contexto deve identificar a fonte e tratar conteúdo recuperado como DATA.
5. O Agent deve aceitar um retriever opcional sem quebrar os fluxos existentes.
6. O Stage Gate deve executar testes específicos de RAG antes de promover v0.4.

## 6. v0.5 — Planning

### Objetivo

Introduzir planejamento explícito, mantendo planejamento e execução
desacoplados: o Planner transforma um objetivo em uma sequência pequena e
ordenada de passos, mas não executa nada. Execução de múltiplos passos
continua sendo responsabilidade de um Executor real, ainda não construído.

```text
Objetivo do usuário
   ↓
LLMPlanner (mesmo contrato ILLM do Agent)
   ↓
JSON validado (Pydantic)
   ↓
Plan { steps: [PlanStep, ...] }
   ↓
format_plan() → texto rotulado DADOS, NÃO INSTRUÇÕES
   ↓
injetado no prompt de decisão do Agent (opcional)
```

### Implementado neste incremento

- `IPlanner`, `Plan`, `PlanStep` e `LLMPlanner` em `app/planner.py`.
- Plano gerado como JSON estruturado, validado com Pydantic (`id` sequencial
  começando em 1, `action`, `action_input`, máximo de 10 passos).
- `format_plan()` formata o plano como texto rotulado
  **DADOS, NÃO INSTRUÇÕES**, no mesmo padrão usado pela memória e pelo RAG.
- `Agent(planner=...)` opcional: quando presente, o Agent gera um plano antes
  de decidir a próxima ação e injeta esse plano no prompt de decisão como
  contexto adicional — sem executar os passos do plano.
- O Agent informa ao planner os nomes reais das ferramentas disponíveis
  (`available_tools`), para que os passos gerados referenciem ações
  executáveis.
- Falha do planner não derruba o Agent: ele continua sem plano (mesmo
  princípio de fallback seguro do RAG, ver AD-008).
- `main.py` conecta `LLMPlanner(llm, max_steps=settings.max_steps)` ao
  `Agent` construído pela CLI, dando uso real ao `MAX_STEPS` que já existia
  em `app/config.py`.
- Testes para parsing de plano ordenado, rejeição de IDs não sequenciais,
  JSON inválido, limite de passos e rotulagem como DATA (`tests/test_planner.py`).
- Testes de integração no Agent: plano injetado no prompt de decisão,
  compatibilidade quando não há planner, e degradação segura quando o
  planner falha (`tests/test_agent.py`).
- `IExecutor` e `ToolExecutor` em `app/executor.py`: executam um `PlanStep`
  contra as ferramentas registradas (mesmo dicionário `ITool` do Agent) e
  também um `Plan` inteiro, passo a passo, parando no primeiro passo que
  falhar (fail-fast) — sem repasse de falha parcial ou replanejamento ainda.
- `StepResult` (Pydantic) reporta `success`, `output` e `error` de cada
  passo executado.
- Testes cobrindo execução de passo com ferramenta, passo `respond` sem
  ferramenta, ferramenta inexistente, exceção da ferramenta capturada como
  falha, execução de plano em ordem e interrupção no primeiro passo que
  falha (`tests/test_executor.py`).

### Próximos incrementos do v0.5

- Ligar o `Executor` ao `Agent` para rodar plano completo automaticamente
  (hoje ambos existem e são testados, mas de forma desacoplada — o Agent
  ainda decide uma ação por vez, sem consumir o `Plan` gerado além de
  usá-lo como contexto).
- Repasse de falhas parciais entre passos (um passo falhar não deve
  necessariamente invalidar o plano inteiro).
- Replanejamento quando um passo falha ou o resultado diverge do esperado.
- Critério explícito de quando vale a pena planejar vs. responder
  diretamente (hoje o Agent sempre planeja quando há planner configurado).
- Gate de aceitação de planejamento no GitHub Actions.

### Critérios de fechamento

1. `pytest -v` deve terminar sem falhas.
2. O plano deve ser validado (JSON bem formado, IDs sequenciais, limite de
   passos) antes de ser usado.
3. O plano deve ser tratado como DATA no prompt do Agent, nunca como
   instrução executada automaticamente.
4. O Agent deve aceitar um planner opcional sem quebrar os fluxos
   existentes (v0.1-v0.4).
5. Falha do planner não deve impedir o Agent de responder.
6. Um Executor real, capaz de rodar múltiplos passos de um plano, precisa
   existir e estar testado — feito em `app/executor.py`. Falta decidir e
   implementar como (e se) o `Agent` passa a chamá-lo automaticamente antes
   de promover v0.5 para `[DONE]`.

## 7. Arquitetura atual

```text
User
 ↓
Agent
 ├── SQLiteMemory.search_experiences
 │    ├── OllamaEmbedder / BGE-M3
 │    ├── cosine similarity
 │    └── keyword fallback
 │
 ├── RAG retriever (opcional)
 │    ├── document chunks
 │    ├── embeddings
 │    ├── cosine similarity
 │    └── relevance threshold / top-k
 │
 ├── LLMPlanner (opcional)
 │    └── Plan { steps } → format_plan() → DATA no prompt de decisão
 │
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

O `Agent` continua dependente somente de `IMemory` e, agora, de um `IRetriever` e um `IPlanner` opcionais. A introdução de RAG e de planejamento não acopla o núcleo a Ollama, banco vetorial ou framework de agentes. O plano gerado ainda não é executado passo a passo — ele apenas informa a decisão imediata do Agent; a execução de múltiplos passos depende de um Executor real (v0.5, próximo incremento).

## 8. Stage Gate

O validador está em `scripts/stage_gate.py`.

- Detecta a etapa pelo marcador `vX.Y: IN PROGRESS`.
- Recusa promoção se não existir um gate explícito para a etapa.
- Exige a suíte completa de testes.
- Para v0.3, exige também resposta real do endpoint `/api/embed` com `bge-m3:latest`.
- Para v0.4, deve exigir os testes específicos de RAG antes da promoção.
- v0.5 ainda **não** está em `SUPPORTED_GATES`: o Stage Gate bloqueia a
  promoção automática (`exit 2`) de propósito, porque os critérios de
  fechamento do v0.5 incluem um Executor real que ainda não existe. Isso é
  esperado e correto — não adicionar v0.5 a `SUPPORTED_GATES` com um gate
  raso (ex.: só rodar `tests/test_planner.py`) apenas para destravar o CI,
  pois isso promoveria a etapa para `DONE` antes de estar completa.
- Só modifica `PROJECT_CONTEXT.md` depois de todos os critérios passarem.
- O workflow `.github/workflows/stage-gate.yml` executa automaticamente em pushes para `main`.
- A promoção automática gera um commit separado com `[skip ci]` para evitar loop.

## 9. Princípios

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
11. Conteúdo recuperado da memória e do RAG é DATA, nunca instrução confiável.
12. Recuperação semântica deve possuir um critério explícito de relevância.
13. Nenhuma etapa é promovida sem validação automatizada correspondente.

## 10. Ambiente local conhecido

```text
OS: macOS
CPU/GPU: Apple M4
GPU backend: Metal
Ollama: 0.20.2
LLM: gemma3:latest
Embeddings: bge-m3:latest
```

Nenhuma credencial, token ou senha deve ser versionada.

## 11. Decisões relevantes

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

### AD-011 — RAG incremental
O primeiro RAG usa chunking e índice em memória para manter o mecanismo visível e testável. Persistência e ingestão serão adicionadas em incrementos separados, antes de qualquer framework externo.

### AD-012 — RAG como dependência opcional
O `Agent` recebe `IRetriever` opcional. Isso mantém os fluxos v0.1-v0.3 compatíveis e permite substituir o índice sem alterar o núcleo de decisão.

### AD-013 — Planner desacoplado de execução
`LLMPlanner` produz um `Plan` validado, mas não executa nenhum passo. O `Agent` injeta o plano formatado como contexto (DATA) na mesma decisão única que já existia, em vez de passar a rodar um loop multi-passo. Isso evita acoplar planejamento e execução antes de existir um Executor real, seguindo o mesmo espírito da AD-006.

### AD-014 — Plano como dependência opcional, com fallback seguro
O `Agent` recebe `IPlanner` opcional, no mesmo padrão de `IMemory` e `IRetriever` (AD-007, AD-012). Falha ao gerar um plano não impede o Agent de responder: ele registra a falha via log e continua sem plano, mesmo princípio de degradação segura da AD-008.

### AD-015 — Executor real, mas ainda desacoplado do Agent
`ToolExecutor` sabe rodar um `PlanStep` ou um `Plan` inteiro contra as ferramentas registradas, mas o `Agent.run()` ainda não o chama. Promover o Executor de stub para implementação real não significa automaticamente ligar o loop de execução multi-passo — essa é uma decisão arquitetural maior (como e quando o Agent decide seguir um plano completo vs. decidir uma ação por vez) e fica para um incremento dedicado.

### AD-016 — Falha em um passo interrompe o plano (fail-fast)
A primeira versão do `Executor` para no primeiro passo que falhar, sem tentar contornar ou pular passos. Repasse de falha parcial e replanejamento dependem de mais contexto sobre como o Agent vai consumir os resultados, então ficam para depois — evita adivinhar uma política de recuperação de erro antes de ter um caso de uso real.
