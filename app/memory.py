"""Experience memory with optional semantic retrieval via BGE-M3/Ollama."""
from __future__ import annotations

import json
import logging
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Protocol

import requests
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)


class Experience(BaseModel):
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


class IEmbedder(Protocol):
    def embed(self, text: str) -> list[float]: ...


class OllamaEmbedder:
    """Embeddings locais através do endpoint /api/embed do Ollama."""

    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None,
                 timeout: Optional[int] = None) -> None:
        self.model = model or settings.embedding_model
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.timeout = timeout or settings.llm_timeout

    def embed(self, text: str) -> list[float]:
        response = requests.post(
            f"{self.base_url}/api/embed",
            json={"model": self.model, "input": text},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings")
        if not embeddings or not isinstance(embeddings[0], list):
            raise ValueError("Ollama não retornou um embedding válido")
        return [float(value) for value in embeddings[0]]


class IMemory(Protocol):
    def store_experience(self, experience: Experience) -> int: ...
    def get_experience(self, experience_id: int) -> Optional[Experience]: ...
    def search_experiences(self, query: str, limit: int = 5) -> list[Experience]: ...


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
    metadata TEXT,
    embedding TEXT,
    embedding_model TEXT
)
"""


class SQLiteMemory:
    """SQLite-backed memory with optional semantic vector retrieval.

    Without an embedder, legacy keyword search remains available. With an
    embedder, new experiences are vectorized and queries use cosine similarity.
    Existing databases are migrated in place and legacy rows remain searchable
    through keyword fallback until they are embedded.
    """

    def __init__(self, db_path: str = "data/memory.db", embedder: Optional[IEmbedder] = None) -> None:
        self.db_path = db_path
        self.embedder = embedder
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        self._conn.close()

    def _init_schema(self) -> None:
        self._conn.execute(_SCHEMA)
        columns = {row[1] for row in self._conn.execute("PRAGMA table_info(experiences)")}
        if "embedding" not in columns:
            self._conn.execute("ALTER TABLE experiences ADD COLUMN embedding TEXT")
        if "embedding_model" not in columns:
            self._conn.execute("ALTER TABLE experiences ADD COLUMN embedding_model TEXT")
        self._conn.commit()

    @staticmethod
    def _experience_text(experience: Experience) -> str:
        parts = [experience.task, experience.plan, experience.action, experience.tool,
                 experience.result, experience.evaluation]
        return "\n".join(part for part in parts if part)

    def store_experience(self, experience: Experience) -> int:
        embedding: Optional[list[float]] = None
        embedding_model: Optional[str] = None
        if self.embedder is not None:
            try:
                embedding = self.embedder.embed(self._experience_text(experience))
                embedding_model = getattr(self.embedder, "model", None)
            except Exception:
                logger.exception("MEMORY.embedding | falha; armazenando sem vetor")

        cursor = self._conn.execute(
            """
            INSERT INTO experiences
                (created_at, task, plan, action, tool, input, result,
                 evaluation, success, importance, metadata, embedding, embedding_model)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                experience.created_at, experience.task, experience.plan,
                experience.action, experience.tool,
                json.dumps(experience.input) if experience.input is not None else None,
                experience.result, experience.evaluation,
                None if experience.success is None else int(experience.success),
                experience.importance,
                json.dumps(experience.metadata) if experience.metadata is not None else None,
                json.dumps(embedding) if embedding is not None else None,
                embedding_model,
            ),
        )
        self._conn.commit()
        experience_id = int(cursor.lastrowid)
        logger.info("MEMORY.store | id=%s task=%r success=%s embedded=%s",
                    experience_id, experience.task, experience.success, embedding is not None)
        return experience_id

    def get_experience(self, experience_id: int) -> Optional[Experience]:
        row = self._conn.execute("SELECT * FROM experiences WHERE id = ?", (experience_id,)).fetchone()
        return self._row_to_experience(row) if row is not None else None

    def search_experiences(self, query: str, limit: int = 5) -> list[Experience]:
        if not query.strip() or limit <= 0:
            return []
        if self.embedder is not None:
            try:
                return self._semantic_search(query, limit)
            except Exception:
                logger.exception("MEMORY.semantic_search | falha; usando busca por palavra-chave")
        return self._keyword_search(query, limit)

    def _semantic_search(self, query: str, limit: int) -> list[Experience]:
        query_vector = self.embedder.embed(query)  # type: ignore[union-attr]
        rows = self._conn.execute("SELECT * FROM experiences WHERE embedding IS NOT NULL").fetchall()
        if not rows:
            return self._keyword_search(query, limit)

        scored: list[tuple[float, sqlite3.Row]] = []
        for row in rows:
            vector = json.loads(row["embedding"])
            scored.append((self._cosine_similarity(query_vector, vector), row))
        scored.sort(key=lambda item: item[0], reverse=True)
        results = [self._row_to_experience(row) for score, row in scored[:limit] if score > 0]
        logger.info("MEMORY.semantic_search | query=%r candidates=%d returned=%d",
                    query, len(rows), len(results))
        return results

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b) or not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _keyword_search(self, query: str, limit: int) -> list[Experience]:
        terms = [term.lower() for term in query.split() if term]
        if not terms:
            return []
        clauses = " OR ".join(
            "(lower(task) LIKE ? OR lower(result) LIKE ? OR lower(evaluation) LIKE ?)"
            for _ in terms
        )
        params: list[str] = []
        for term in terms:
            pattern = f"%{term}%"
            params.extend([pattern, pattern, pattern])
        rows = self._conn.execute(
            f"SELECT * FROM experiences WHERE {clauses} ORDER BY created_at DESC", params
        ).fetchall()

        def score(row: sqlite3.Row) -> int:
            haystack = " ".join((row["task"] or "", row["result"] or "", row["evaluation"] or "")).lower()
            return sum(1 for term in terms if term in haystack)

        ranked = sorted(rows, key=score, reverse=True)
        return [self._row_to_experience(row) for row in ranked[:limit]]

    @staticmethod
    def _row_to_experience(row: sqlite3.Row) -> Experience:
        return Experience(
            id=row["id"], created_at=row["created_at"], task=row["task"],
            plan=row["plan"], action=row["action"], tool=row["tool"],
            input=json.loads(row["input"]) if row["input"] else None,
            result=row["result"], evaluation=row["evaluation"],
            success=None if row["success"] is None else bool(row["success"]),
            importance=row["importance"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else None,
        )
