"""
Agent - núcleo do v0.1.

Fluxo implementado (subconjunto do ciclo cognitivo completo, que será
expandido nos próximos estágios):

    User -> Agent -> LLM (decisão) -> Tool selection -> Tool.run()
         -> Observation -> LLM (resposta final) -> Response

Planner, Executor e Evaluator como módulos dedicados ainda não entram
aqui: a "decisão" e a "execução" do v0.1 são simples o suficiente para
viver dentro do próprio Agent. Extrair isso para os módulos stub já
criados (app/planner.py, app/executor.py, app/evaluator.py) é trabalho
do v0.2/v0.3/v0.4, quando houver lógica real (múltiplos passos,
replanejamento, avaliação de qualidade) que justifique a separação.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from pydantic import BaseModel, Field, ValidationError

from app.llm import ILLM
from app.tools.base import ITool

logger = logging.getLogger(__name__)


DECISION_SYSTEM_PROMPT = """Você é um agente de IA com acesso às seguintes ferramentas:

{tools_description}

Dado o pedido do usuário, decida se deve usar uma ferramenta ou responder diretamente.
Responda APENAS com um JSON válido, sem nenhum texto antes ou depois, no formato:

{{"action": "<nome_da_ferramenta_ou_respond>", "action_input": {{...}}, "reasoning": "breve justificativa"}}

Se action for "respond", action_input deve conter {{"answer": "sua resposta direta ao usuário"}}.
Se action for o nome de uma ferramenta, action_input deve conter os parâmetros dela.
"""

FINAL_ANSWER_SYSTEM_PROMPT = """Você é um agente de IA. Você acabou de executar uma ferramenta
para atender ao pedido do usuário e obteve o resultado abaixo.

Resultado da ferramenta:
{observation}

Use esse resultado para responder à pergunta original do usuário de forma clara, direta e em
linguagem natural. Não repita o JSON, não mencione ferramentas internas - apenas responda.
"""


class AgentDecision(BaseModel):
    action: str
    action_input: dict = Field(default_factory=dict)
    reasoning: Optional[str] = None


class AgentResult(BaseModel):
    response: str
    tool_used: Optional[str] = None
    tool_output: Optional[str] = None
    raw_decision: Optional[str] = None


class Agent:
    def __init__(self, llm: ILLM, tools: list[ITool]) -> None:
        self.llm = llm
        self.tools: dict[str, ITool] = {tool.name: tool for tool in tools}

    def _tools_description(self) -> str:
        if not self.tools:
            return "(nenhuma ferramenta disponível)"
        return "\n".join(f"- {t.name}: {t.description}" for t in self.tools.values())

    def run(self, user_input: str) -> AgentResult:
        logger.info("PERCEPTION | input=%r", user_input)

        decision = self._decide(user_input)

        if decision is None:
            # Não foi possível interpretar a decisão do LLM como JSON válido.
            # Degrada de forma segura: trata a saída bruta como resposta direta.
            raw = self._last_raw_decision
            logger.warning("REASONING | decisão não pôde ser parseada, tratando como resposta direta")
            return AgentResult(response=raw, raw_decision=raw)

        if decision.action == "respond" or decision.action not in self.tools:
            answer = decision.action_input.get("answer") or self._last_raw_decision
            logger.info("FINAL RESPONSE (direta) | %r", answer)
            return AgentResult(response=answer, raw_decision=self._last_raw_decision)

        return self._act_and_respond(user_input, decision)

    def _decide(self, user_input: str) -> Optional[AgentDecision]:
        system_prompt = DECISION_SYSTEM_PROMPT.format(tools_description=self._tools_description())
        raw_decision = self.llm.complete(prompt=user_input, system=system_prompt)
        self._last_raw_decision = raw_decision
        logger.info("REASONING/PLANNING | raw_decision=%r", raw_decision)

        try:
            return AgentDecision.model_validate_json(raw_decision)
        except (ValidationError, json.JSONDecodeError):
            return None

    def _act_and_respond(self, user_input: str, decision: AgentDecision) -> AgentResult:
        logger.info("TOOL SELECTION | tool=%s input=%s", decision.action, decision.action_input)
        tool = self.tools[decision.action]

        try:
            observation = tool.run(**decision.action_input)
        except Exception as exc:  # ferramenta com erro não deve derrubar o agente
            observation = f"Erro ao executar a ferramenta '{decision.action}': {exc}"
            logger.exception("EXECUTION | erro na ferramenta %s", decision.action)

        logger.info("OBSERVATION | %s", observation)

        final_system_prompt = FINAL_ANSWER_SYSTEM_PROMPT.format(observation=observation)
        final_answer = self.llm.complete(prompt=user_input, system=final_system_prompt)
        logger.info("EVALUATION/FINAL RESPONSE | %r", final_answer)

        return AgentResult(
            response=final_answer,
            tool_used=decision.action,
            tool_output=observation,
            raw_decision=self._last_raw_decision,
        )
