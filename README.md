# Alpha7 AI

## Alpha7 Retail — compras inteligentes para lojas de moda e lingerie

> **Do estoque ao pedido de compra, com IA sob controle.**

O Alpha7 está evoluindo de uma plataforma genérica de agentes autônomos para produtos verticais. O primeiro MVP comercial é o **Alpha7 Retail**: um agente de compras que analisa estoque e vendas, calcula reposição, prepara pedidos e mantém aprovação e regras de negócio sob controle do lojista.

### Fluxo do produto

```text
ESTOQUE + VENDAS + FORNECEDORES
              ↓
        PREVISÃO DE DEMANDA
              ↓
      NECESSIDADE DE REPOSIÇÃO
              ↓
       RECOMENDAÇÃO DE COMPRA
              ↓
          APROVAÇÃO
              ↓
       PEDIDO AO FORNECEDOR
              ↓
             AUDIT
```

### Exemplo

```text
Produto: Sutiã Rendado Preto — tamanho 40
Estoque: 7 unidades
Vendas médias: 2,73/dia
Lead time: 8 dias
Estoque de segurança: 7 dias

Alpha7 recomenda: comprar 34 unidades
Custo estimado: €278,80
Urgência: alta

[ APROVAR COMPRA ]  [ REJEITAR ]
```

A quantidade recomendada é calculada por regras determinísticas. A IA pode interpretar, explicar e orquestrar o processo, mas não pode ultrapassar as políticas definidas pelo proprietário.

## O que o Alpha7 Retail resolve

- Reduz risco de ruptura de estoque.
- Identifica produtos que precisam de reposição.
- Considera vendas médias, lead time e estoque de segurança.
- Agrupa recomendações por fornecedor.
- Calcula investimento necessário.
- Prepara pedidos de compra para aprovação.
- Mantém rastreabilidade das decisões do agente.
- Pode evoluir para integração com ERP, POS, Shopify, WooCommerce, PrestaShop e APIs de fornecedores.

## Demo do MVP

```bash
python -m app.retail.demo
```

Testes:

```bash
pytest -v
```

## Plataforma Alpha7

**Alpha7** é uma plataforma local-first para construir, executar, controlar e auditar agentes autônomos. O princípio central permanece:

> **Autonomia sem perder o controle.**

O modelo propõe. O sistema controla. O usuário define a autoridade. A plataforma registra o que aconteceu.

### Arquitetura

```text
                         ALPHA7
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
          AGENTES        CONTROLE      AVALIAÇÃO
             │              │              │
             └──────────────┼──────────────┘
                            ↓
                       EXECUÇÃO
                            ↓
                        MEMÓRIA
                            ↓
                       EXPERIÊNCIA
```

### Runtime

- Agent
- Planner
- Plan validation
- Executor
- Tools
- Bounded autonomous execution

### Inteligência

- LLM local
- Memória
- Memória semântica
- RAG
- Conhecimento
- Experiência

### Controle

- Políticas comportamentais
- Permissões de ferramentas
- Aprovações
- Limites de iteração
- Configuração de agentes

### Avaliação e confiança

- Avaliação determinística
- LLM Judge
- Reflection
- Auditabilidade
- Replay
- Benchmarks

## Modelo de confiança

1. O usuário define a missão e a política.
2. O modelo propõe ações, mas não define sua própria autoridade.
3. Memória e RAG são dados, não instruções.
4. Planos são validados antes da execução.
5. Ferramentas podem exigir aprovação explícita.
6. Avaliação é separada da execução.
7. Reflection não pode ignorar políticas.
8. Retentativas são limitadas.
9. Aprendizado exige dados aprovados e medição.
10. O sistema prefere falhar fechado a ultrapassar sua autoridade silenciosamente.

## Technology Battery

**Score inicial: 61 / 100.** Este indicador mede capacidade tecnológica, não percentual de conclusão. A documentação completa está em `docs/TECHNOLOGY_BATTERY.md`.

## Stack

- Python 3.12
- Ollama
- Gemma 3
- BGE-M3
- SQLite
- Pydantic
- pytest

A arquitetura atual não exige uma API de modelo paga.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Modelos locais:

```bash
ollama serve
ollama pull gemma3:latest
ollama pull bge-m3:latest
```

Runtime atual:

```bash
python main.py
```

## Roadmap comercial

```text
MVP Retail
   ↓
API REST
   ↓
Dashboard
   ↓
Autenticação / RBAC
   ↓
Approvals + Audit
   ↓
Docker
   ↓
Integrações ERP / E-commerce
   ↓
Multi-loja
   ↓
Cloud / Managed Service
```

O objetivo é usar o Alpha7 Core como motor e construir produtos verticais em cima dele, começando pelo varejo de moda e lingerie.

## Documentação

- `docs/PRODUCT_VISION.md` — visão da plataforma.
- `docs/TECHNOLOGY_BATTERY.md` — metodologia de avaliação.
- `docs/BRANDING.md` — estratégia de marca.
