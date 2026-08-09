# PROJECT_CONTEXT.md — Zero-Agent

> Este documento é a fonte de verdade sobre o estado do projeto. Deve
> refletir o **código real**, não intenções. Se divergir do código, o código
> está certo e este arquivo deve ser corrigido.

---

## 1. Identidade

**Nome:** Zero-Agent

**Objetivo:** construir progressivamente, começando praticamente do zero,
um sistema de IA em Python capaz de perceber, raciocinar, planejar,
utilizar ferramentas, executar ações, avaliar resultados, manter memória
e posteriormente aprender com experiências.

O projeto é também um estudo experimental: entender cada mecanismo antes
de usar abstrações de terceiros e medir a evolução de forma incremental.

---

## 2. Estado atual

```text
Version: v0.2
Status: DONE
NEXT MILESTONE: v0.3 — Semantic Memory / BGE-M3
```

| Componente | Status | Observação |
|---|---|---|
| Python 3.12 + estrutura | IMPLEMENTED | `app/`, `tests/`, `main.py` |
| `ILLM` | IMPLEMENTED | Abstração do provedor LLM |
| `OllamaProvider` | IMPLEMENTED | HTTP para Ollama |
| Gemma 3 | IMPLEMENTED | Modelo local configurável |
| `Agent` | IMPLEMENTED | Decisão → tool → resposta |
| `FileSystemTool` | IMPLEMENTED | `list` / `read`, restrito a root |
| Testes automatizados | IMPLEMENTED | Suíte existente validando v0.2 |
| `SQLiteMemory` | IMPLEMENTED | Store/get/search por palavra-chave |
| Memory ↔ Agent | IMPLEMENTED | Consulta antes da decisão e grava após execução |
| `SimpleEvaluator` | IMPLEMENTED | Determinístico, sem LLM |
| BGE-M3 | NOT IMPLEMENTED | Próximo milestone |
| Embeddings | NOT IMPLEMENTED | Próximo milestone |
| Busca semântica | NOT IMPLEMENTED | Próximo milestone |
| RAG | NOT IMPLEMENTED | v0.4 |
| Planner | STUB | Interface sem lógica real |
| Executor | STUB | Interface sem lógica real |
| Reflection | NOT IMPLEMENTED | v0.6 |
| Autonomous loops | NOT IMPLEMENTED | v0.7 |
| Multi-agent | NOT IMPLEMENTED | v0.8 |
| Multimodal | NOT IMPLEMENTED | v0.9 |
| Web UI | NOT IMPLEMENTED | Fora das etapas atuais |
| Fine-tuning / treinamento / RL | NOT IMPLEMENTED | Etapas futuras |

---

## 3. Roadmap e controle de etapas

```text
v0.1  Agent básico                    [DONE]
v0.2  Experience Memory               [DONE]
v0.3  Semantic Memory / BGE-M3        [NEXT]
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

### Regra obrigatória de progressão

Toda vez que uma etapa for concluída:

1. Verificar o código real.
2. Executar a suíte completa de testes.
3. Confirmar que os critérios da etapa foram realmente atendidos.
4. Marcar a etapa como `[DONE]` neste arquivo e no `README.md`.
5. Registrar resumidamente o que foi implementado.
6. Marcar a próxima etapa como `[NEXT]`.
7. Atualizar arquitetura/decisões se necessário.
8. Só então considerar a etapa encerrada.

**Nunca marcar uma etapa como DONE apenas porque o código foi escrito.**
Ela precisa funcionar e ter testes.

Uma mudança de roadmap também deve ser registrada aqui antes de começar
uma etapa diferente da atualmente marcada como `[NEXT]`.

---

## 4. Ambiente local conhecido

```text
OS: macOS
CPU/GPU: Apple M4
GPU backend: Metal
GPU memory reported by Ollama: ~11.8 GiB
Ollama: 0.20.2
```

Modelos locais conhecidos:

```text
gemma3:latest   (LLM principal)
bge-m3:latest   (disponível, ainda não integrado)
```

Nenhuma credencial, token ou senha deve ser versionada. Segredos ficam
somente no `.env` local, que é git-ignored.

---

## 5. Arquitetura atual

```text
User
 ↓
Agent
 ↓
Memory.search_experiences
 ↓
LLM (decisão com contexto de memória)
 ↓
Tool selection → Tool.run() → Observation
 ↓
LLM (resposta final)
 ↓
SimpleEvaluator
 ↓
Memory.store_experience
 ↓
Response
```

A memória atual é SQLite e usa busca por palavra-chave (`LIKE` + ranking
em Python). A interface `IMemory` deve permanecer estável durante o v0.3,
permitindo substituir a recuperação por similaridade semântica sem exigir
alterações no `Agent`.

---

## 6. Próximo milestone — v0.3

### Semantic Memory / BGE-M3

Objetivo:

```text
SQLiteMemory
    ↓
keyword search (atual)
    ↓
BGE-M3 embeddings
    ↓
semantic similarity
    ↓
semantic memory retrieval
```

Incrementos esperados:

1. Criar abstração de embeddings.
2. Implementar provider BGE-M3 via Ollama ou mecanismo local apropriado.
3. Criar embeddings das experiências persistidas.
4. Implementar recuperação por similaridade.
5. Preservar `IMemory` para não acoplar o Agent à implementação.
6. Criar testes determinísticos para a camada de embeddings/recuperação.
7. Integrar ao Agent.
8. Rodar a suíte completa.
9. Atualizar este arquivo e o README para concluir o v0.3.

Não implementar RAG, Planner real, Multi-agent ou outras etapas enquanto
o v0.3 não estiver concluído, salvo mudança explícita do roadmap.

---

## 7. Princípios

1. Simplicidade antes de abstração excessiva.
2. Compreensão antes de frameworks.
3. Implementação incremental.
4. Componentes substituíveis via interfaces/Protocols.
5. Testes em cada estágio.
6. Observabilidade.
7. Experimentação mensurável.
8. Nenhuma funcionalidade sem necessidade real.
9. Memória não é treinamento.
10. Modelos existentes primeiro; modelos próprios depois.
11. Documentação acompanha o código em cada etapa.

---

## 8. Decisões arquiteturais relevantes

### AD-001 — Python
Escolhido pelo objetivo de longo prazo envolvendo agentes, embeddings,
PyTorch, Transformers, fine-tuning e pesquisa experimental.

### AD-002 — Ollama
Runtime inicial local, abstraído por `ILLM`.

### AD-003 — Gemma 3
LLM inicial e substituível; não é o Zero-Agent. O agente é o sistema que
usa o modelo e implementa percepção, decisão, ferramentas, avaliação e
memória.

### AD-004 — BGE-M3
Escolhido para o próximo estágio de memória semântica. A busca por
palavras-chave foi implementada primeiro para validar persistência e manter
a abstração desacoplada.

### AD-005 — Sem frameworks de agentes
LangChain, CrewAI, AutoGen e similares não entram no núcleo enquanto os
mecanismos fundamentais estiverem sendo estudados.

### AD-006 — Planner/Executor
Continuam como stubs enquanto decisões de múltiplos passos,
replanejamento e execução estruturada ainda não justificarem sua
extração para componentes reais.

### AD-007 — Toda execução real vira experiência
O Agent grava experiências após respostas diretas, uso de ferramenta ou
falhas de decisão, sem inventar experiências.

### AD-008 — Memory opcional
O Agent funciona sem memória para preservar compatibilidade com o v0.1.

---

## 9. Modelo mental

```text
MODEL ≠ RUNTIME ≠ AGENT

Gemma 3    = modelo / pesos
Ollama     = runtime
Zero-Agent = sistema que usa o modelo e implementa o ciclo do agente
```

---

## 10. Regra para novas sessões de IA

Uma nova sessão deve:

```text
1. Ler AGENTS.md
2. Ler PROJECT_CONTEXT.md
3. Ler README.md
4. Verificar git status / histórico
5. Inspecionar o código real
6. Identificar [NEXT]
7. Trabalhar somente no próximo incremento pequeno
8. Testar
9. Documentar
10. Parar e aguardar autorização antes de outro incremento significativo
```

O repositório, e não o histórico de conversa, é a fonte de verdade.
