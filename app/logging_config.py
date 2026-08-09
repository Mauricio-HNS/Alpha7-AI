"""
Setup de logging.

O ciclo cognitivo do agente (perception -> reasoning -> planning ->
tool selection -> execution -> observation -> evaluation -> memory)
precisa ser observável. Cada etapa relevante é logada em app/agent.py
usando o logger configurado aqui.
"""
from __future__ import annotations

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
