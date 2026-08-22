"""Export approved experiences into a training-ready JSONL dataset.

This is deliberately separate from the model. Memory is not silently converted
into weight updates; only explicitly approved experiences become training data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from app.memory import Experience


def export_experiences(
    experiences: Iterable[Experience],
    output_path: str = "data/training/approved.jsonl",
) -> int:
    """Export successful, useful experiences as instruction/response examples."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with path.open("w", encoding="utf-8") as handle:
        for experience in experiences:
            if experience.success is not True or experience.importance < 0.6:
                continue
            response = experience.result or ""
            if not response.strip():
                continue
            record = {
                "instruction": experience.task,
                "response": response,
                "metadata": {
                    "experience_id": experience.id,
                    "tool": experience.tool,
                    "evaluation": experience.evaluation,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    return count
