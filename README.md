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
> Esses arquivos, junto com o histórico do Git, são a fonte de verdade do
> projeto — uma nova sessão de IA deve conseguir continuar o trabalho lendo
> apenas eles, sem depender de conversas anteriores.

## Estágio atual: v0.2 (completo) — Experience-based memory

**Importante — memória ≠ treinamento:** este estágio adiciona persistência
de experiências (o que o agente tentou, o que aconteceu, se deu certo) e
recuperação delas para informar decisões futuras. Os parâmetros do LLM
(Gemma 3, via Ollama) **não são alterados** por nada aqui.

O v0.2 está completo: SQLiteMemory, integração com Agent e SimpleEvaluator
estão implementados e testados. A busca ainda é por palavra-chave; a busca
semântica com BGE-M3 é o próximo estágio.

## Ciclo implementado

```text
User -> Agent -> Memory.search_experiences -> LLM (decide, com contexto
     de memória) -> Tool selection -> Tool.run() -> Observation ->
     LLM (resposta final) -> SimpleEvaluator -> Memory.store_experience
     -> Response
```

## Roadmap

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

**Regra do roadmap:** ao concluir uma etapa, o agente de programação deve
atualizar imediatamente este README e o `PROJECT_CONTEXT.md`, marcando a
etapa como `[DONE]`, registrando o que foi realmente implementado e
promovendo a próxima etapa para `[NEXT]`. Nenhuma etapa pode ser marcada
como concluída sem código e testes correspondentes.

### v0.3 — Semantic Memory / BGE-M3

Próxima etapa concreta:

```text
SQLiteMemory
    ↓
keyword search
    ↓
BGE-M3 embeddings
    ↓
semantic similarity
    ↓
semantic memory retrieval
```

O objetivo é substituir a busca por palavra-chave por recuperação semântica,
mantendo a interface `IMemory` estável para que o `Agent` não precise ser
reescrito.

## O que já existe

- Python 3.12+
- Abstração `ILLM`
- `OllamaProvider`
- Gemma 3 via Ollama
- `Agent` com decisão, uso de ferramentas e resposta final
- `FileSystemTool` com `list` / `read`
- `Experience` com Pydantic
- `SQLiteMemory` com `store`, `get` e busca por palavra-chave
- `SimpleEvaluator`
- Integração de memória com o Agent
- Logging estruturado do ciclo cognitivo
- Testes automatizados

## O que ainda não existe

- BGE-M3 integrado ao código
- Embeddings
- Busca semântica
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

## Requisitos

- Python 3.12+
- [Ollama](https://ollama.com) rodando localmente, com um modelo baixado

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Rodando

```bash
ollama serve
python main.py
```

## Testes

```bash
pytest -v
```

Os testes usam mocks/fakes quando dependem do LLM, portanto a suíte não
precisa de um Ollama real para ser determinística e rápida.

## Configuração

| Variável | Default | Descrição |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL do servidor Ollama |
| `OLLAMA_MODEL` | `llama3.2` | Modelo usado |
| `LLM_TIMEOUT` | `60` | Timeout das chamadas ao LLM |
| `MAX_STEPS` | `5` | Limite de passos autônomos futuros |
| `MAX_TOOL_CALLS` | `10` | Limite de chamadas de ferramenta futuras |

## Arquitetura

```text
zero-agent/
├── app/
│   ├── config.py
│   ├── logging_config.py
│   ├── agent.py
│   ├── llm.py
│   ├── memory.py
│   ├── planner.py
│   ├── executor.py
│   ├── evaluator.py
│   └── tools/
│       ├── base.py
│       └── filesystem.py
├── tests/
├── data/
├── main.py
└── requirements.txt
```

O roadmap é experimental e pode ser revisado quando resultados reais
indicarem uma arquitetura melhor. Porém, qualquer alteração deve ser
registrada na documentação antes de avançar para uma etapa diferente.
