# Zero-Agent

Sistema de agente de IA construído do zero, em Python, sem frameworks de
agentes (LangChain, CrewAI, AutoGen, etc.). O objetivo é entender e
implementar manualmente os mecanismos fundamentais de um agente antes de
comparar com soluções prontas.

Este projeto evolui em estágios pequenos e versionados. Cada estágio
precisa funcionar, ter testes, ter documentação e servir de base para o
próximo.

> **Para o estado real e atualizado do projeto, decisões arquiteturais e
> o próximo passo planejado, veja [`PROJECT_CONTEXT.md`](./PROJECT_CONTEXT.md).**
> **Para as regras de trabalho de qualquer agente de programação (Claude,
> Codex, etc.) neste repositório, veja [`AGENTS.md`](./AGENTS.md).**
>
> Esses dois arquivos, junto com o histórico do Git, são a fonte de
> verdade do projeto — uma nova sessão de IA deve conseguir continuar o
> trabalho lendo apenas eles, sem depender de conversas anteriores.

## Estágio atual: v0.2 (incremento 1/2) — Experience-based memory

**Importante — memória ≠ treinamento:** este estágio adiciona persistência
de experiências (o que o agente tentou, o que aconteceu, se deu certo).
Os parâmetros do LLM (Gemma 3, via Ollama) **não são alterados** por nada
aqui. Chamamos isso de *memory-based learning* ou *experience-based
memory* - nunca de "treinamento" ou "fine-tuning", que são coisas
diferentes e vêm em estágios futuros (v2.x/v3.x no roadmap).

Este primeiro incremento entrega **apenas a camada de persistência**:

```text
app/memory.py
├── Experience        # modelo (Pydantic) de uma experiência real
├── IMemory            # protocolo: store_experience / get_experience / search_experiences
└── SQLiteMemory        # implementação sobre SQLite
```

- `Experience` exige `task` (não é possível criar uma "experiência" sem
  saber qual tarefa ela representa - isso é validado pelo Pydantic).
- `search_experiences` usa busca por palavra-chave (SQL `LIKE` + ranking
  em Python por número de termos coincidentes) - **sem embeddings e sem
  vector database ainda**. Isso é proposital: a abstração (`IMemory`) já
  permite trocar a implementação de busca depois (ex.: BGE-M3 +
  similaridade) sem tocar em quem consome a memória.
- Memória é **dado**, nunca instrução: nada neste módulo interpreta ou
  executa o conteúdo recuperado do banco.

**O que ainda não existe (próximo incremento):** integração com o
`Agent` (consultar memória antes de decidir, salvar experiência depois de
executar). Hoje `SQLiteMemory` funciona de forma isolada, validada só por
testes diretos (`tests/test_memory.py`).

## Estágio anterior: v0.1 — Agente mínimo

Fluxo implementado:

```text
Usuário
   ↓
Agent
   ↓
LLM (decide: responder direto ou usar uma ferramenta)
   ↓
FileSystemTool (list / read)
   ↓
Observation
   ↓
LLM (resposta final em linguagem natural)
   ↓
Resposta ao usuário
```

O agente **executa a ferramenta de verdade** — nada de respostas simuladas
ou resultados falsos injetados no prompt.

### O que NÃO está no v0.1 (de propósito)

Memória de longo prazo, RAG, múltiplos agentes, visão, voz, treinamento,
interface web, ShellTool. Cada um entra em um estágio futuro, conforme o
roadmap.

`planner.py`, `executor.py` e `evaluator.py` existem apenas como
**interfaces stub** (protocolos, sem lógica) — a lógica real de decisão e
execução do v0.1 vive dentro de `app/agent.py`, por ser simples demais
para justificar módulos separados ainda. Isso evita retrabalho quando as
implementações reais chegarem (v0.2/v0.3/v0.4).

## Requisitos

- Python 3.12+
- [Ollama](https://ollama.com) rodando localmente, com um modelo baixado
  (ex.: `ollama pull llama3.2`)

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # opcional, os defaults já funcionam
```

## Rodando

Em um terminal, garanta que o Ollama está rodando:

```bash
ollama serve
```

Em outro terminal:

```bash
python main.py
```

Experimente:

```text
Você: Liste os arquivos deste projeto.
```

## Testes

```bash
pytest -v
```

Os testes de `llm.py` e `agent.py` usam mocks/fakes — **não** exigem um
Ollama real rodando. Isso é intencional: testes automatizados precisam
ser determinísticos e rápidos.

## Configuração

Todas as configurações vêm de variáveis de ambiente (ver `app/config.py`
e `.env.example`):

| Variável | Default | Descrição |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL do servidor Ollama |
| `OLLAMA_MODEL` | `llama3.2` | Modelo usado |
| `LLM_TIMEOUT` | `60` | Timeout (segundos) das chamadas ao LLM |
| `MAX_STEPS` | `5` | Limite de passos autônomos (usado a partir de estágios futuros) |
| `MAX_TOOL_CALLS` | `10` | Limite de chamadas de ferramenta (idem) |

## Arquitetura

```text
zero-agent/
├── app/
│   ├── config.py            # configuração via env vars
│   ├── logging_config.py    # logs estruturados (ciclo observável)
│   ├── agent.py             # núcleo: decisão -> ferramenta -> resposta
│   ├── llm.py                # ILLM (protocolo) + OllamaProvider
│   ├── memory.py             # stub (IMemory) - implementação real no v0.5
│   ├── planner.py            # stub (IPlanner) - implementação real no v0.3
│   ├── executor.py           # stub (IExecutor) - implementação real no v0.3
│   ├── evaluator.py          # stub (IEvaluator) - implementação real no v0.4
│   └── tools/
│       ├── base.py           # ITool (protocolo)
│       └── filesystem.py     # list / read, restrito a um diretório raiz
├── tests/
├── data/
├── main.py                   # CLI
└── requirements.txt
```

## Roadmap

```text
v0.1  Agent básico          ← estamos aqui
v0.2  Tools (expandir)
v0.3  Planning
v0.4  Evaluation
v0.5  Memory
v0.6  RAG
v0.7  Reflection
v0.8  Autonomous loops
v0.9  Multi-agent
v1.0  Multimodal
v1.x  Local models
v2.x  Fine-tuning
v3.x  PyTorch
v4.x  Training experiments
v5.x  Custom architectures
```

Este roadmap não é definitivo — cada estágio é revisado com base em
resultados experimentais, não avançado automaticamente.
