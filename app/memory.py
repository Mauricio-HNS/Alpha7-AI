"""
Memória de experiências (Experience-based memory).

IMPORTANTE - memória != treinamento:
Este módulo apenas persiste e recupera registros de execuções reais do
agente (o que foi tentado, o que aconteceu, se deu certo). Os parâmetros
do LLM (Gemma 3, via Ollama) não são alterados por nada aqui. Isso é
"memory-based learning", não fine-tuning nem reinforcement learning.

Escopo deste incremento: apenas a camada de persistência (SQLiteMemory) e
sua interface (IMemory). A integração com o Agent (consultar memória antes
de decidir, salvar experiência depois de executar) é o próximo incremento.

Segurança: memória é DADO, nunca INSTRUÇÃO. Nada aqui interpreta ou
executa conteúdo recuperado do banco - texto recuperado só deve ser usado
como contexto informativo para o LLM (ver docstring de search_experiences).
"""
from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Protocol

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Experience(BaseModel):
    """Representa algo que realmente aconteceu em uma execução do agente.

    Nunca deve ser instanciada com dados inventados - apenas a partir de
    uma execução real (task -> action -> result -> evaluation).
    """

    id: Optional[int] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    task: str
    plan: Optional[str] = None
    action: Optional[str] = None
    tool: Optional[str] = None
    input: Optional[dict[str, Any]] = None
    result: Optional[str] = None
    evaluation: Optional[str] = None
    success: Optional[bool] = None
    importance: float = 0.0
    metadata: Optional[dict[str, Any]] = None


class IMemory(Protocol):
    def store_experience(self, experience: Experience) -> int:
        """Persiste uma experiência e retorna seu id."""
        ...

    def get_experience(self, experience_id: int) -> Optional[Experience]:
        """Recupera uma experiência específica pelo id."""
        ...

    def search_experiences(self, query: str, limit: int = 5) -> list[Experience]:
        """Busca experiências relevantes para uma query (busca por palavra-chave)."""
        ...


_SCHEMA = """
CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    task TEXT NOT NULL,
    plan TEXT,
    action TEXT,
    tool TEXT,
    input TEXT,
    result TEXT,
    evaluation TEXT,
    success INTEGER,
    importance REAL DEFAULT 0.0,
    metadata TEXT
)
"""


class SQLiteMemory:
    """Implementação de IMemory usando SQLite.

    O Agent (e o restante do sistema) não deve conhecer nenhum detalhe de
    SQLite - apenas depende de IMemory.
    """

    def __init__(self, db_path: str = "data/memory.db") -> None:
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        # Conexão única, mantida aberta pela vida da instância. Necessário
        # para ':memory:': cada nova conexão sqlite3 a ':memory:' é um banco
        # totalmente separado, então reabrir conexão por chamada perderia os
        # dados. Para arquivo em disco também é mais eficiente que abrir/
        # fechar uma conexão a cada operação.
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        self._conn.close()

    def _init_schema(self) -> None:
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def store_experience(self, experience: Experience) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO experiences
                (created_at, task, plan, action, tool, input, result,
                 evaluation, success, importance, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                experience.created_at,
                experience.task,
                experience.plan,
                experience.action,
                experience.tool,
                json.dumps(experience.input) if experience.input is not None else None,
                experience.result,
                experience.evaluation,
                None if experience.success is None else int(experience.success),
                experience.importance,
                json.dumps(experience.metadata) if experience.metadata is not None else None,
            ),
        )
        self._conn.commit()
        experience_id = cursor.lastrowid
        logger.info("MEMORY.store | id=%s task=%r success=%s", experience_id, experience.task, experience.success)
        return experience_id

    def get_experience(self, experience_id: int) -> Optional[Experience]:
        row = self._conn.execute("SELECT * FROM experiences WHERE id = ?", (experience_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_experience(row)

    def search_experiences(self, query: str, limit: int = 5) -> list[Experience]:
        """Busca simples por palavra-chave.

        Não é semântica (isso vem em um incremento futuro, com BGE-M3).
        Filtra candidatos que contenham pelo menos um termo da query em
        task/result/evaluation, depois ranqueia em Python pelo número de
        termos que batem (mais termos = mais relevante), desempatando por
        mais recente primeiro.
        """
        terms = [t.lower() for t in query.split() if t]
        if not terms:
            return []

        like_clauses = " OR ".join(
            "(lower(task) LIKE ? OR lower(result) LIKE ? OR lower(evaluation) LIKE ?)" for _ in terms
        )
        params: list[str] = []
        for term in terms:
            pattern = f"%{term}%"
            params.extend([pattern, pattern, pattern])

        sql = f"SELECT * FROM experiences WHERE {like_clauses} ORDER BY created_at DESC"
        rows = self._conn.execute(sql, params).fetchall()

        def score(row: sqlite3.Row) -> int:
            haystack = " ".join(
                (row["task"] or "", row["result"] or "", row["evaluation"] or "")
            ).lower()
            return sum(1 for term in terms if term in haystack)

        ranked = sorted(rows, key=score, reverse=True)
        experiences = [self._row_to_experience(row) for row in ranked[:limit]]
        logger.info("MEMORY.search | query=%r found=%d", query, len(experiences))
        return experiences

    @staticmethod
    def _row_to_experience(row: sqlite3.Row) -> Experience:
        return Experience(
            id=row["id"],
            created_at=row["created_at"],
            task=row["task"],
            plan=row["plan"],
            action=row["action"],
            tool=row["tool"],
            input=json.loads(row["input"]) if row["input"] else None,
            result=row["result"],
            evaluation=row["evaluation"],
            success=None if row["success"] is None else bool(row["success"]),
            importance=row["importance"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else None,
        )
