#!/usr/bin/env python3
"""Run the acceptance gate for the documented milestone.

A stage is promoted only when an explicit gate exists for that stage. This
prevents a green generic test suite from falsely marking future milestones as
complete before their acceptance criteria are defined and tested.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "PROJECT_CONTEXT.md"
SUPPORTED_GATES = {"v0.1", "v0.2", "v0.3"}
ORDER = ["v0.1", "v0.2", "v0.3", "v0.4", "v0.5", "v0.6", "v0.7", "v0.8", "v0.9", "v1.0"]


def run(*args: str) -> None:
    print("$", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def current_stage(text: str) -> str:
    match = re.search(r"NEXT MILESTONE: (v\d+\.\d+)", text)
    if not match:
        raise RuntimeError("NEXT MILESTONE not found in PROJECT_CONTEXT.md")
    return match.group(1)


def advance_context(text: str, stage: str) -> str:
    index = ORDER.index(stage)
    if index + 1 >= len(ORDER):
        return text
    next_stage = ORDER[index + 1]
    text = re.sub(rf"({re.escape(stage)}[^\n]*\[)IN PROGRESS(\])", r"\1DONE\2", text)
    text = re.sub(rf"({re.escape(next_stage)}[^\n]*\[)TODO(\])", r"\1NEXT\2", text)
    text = re.sub(rf"NEXT MILESTONE: {re.escape(stage)}[^\n]*", f"NEXT MILESTONE: {next_stage}", text, count=1)
    return text


def main() -> int:
    text = CONTEXT.read_text(encoding="utf-8")
    stage = current_stage(text)
    print(f"Detected milestone: {stage}")

    if stage not in SUPPORTED_GATES:
        print(f"BLOCKED: no explicit automatic acceptance gate is defined for {stage}.")
        print("Add the stage's real acceptance checks before allowing automatic promotion.")
        return 2

    # Every supported stage requires the complete suite to be green.
    run(sys.executable, "-m", "pytest", "-v")

    if stage == "v0.3":
        # The workflow starts Ollama and loads BGE-M3 before this check.
        run(
            "curl",
            "--fail",
            "--silent",
            "--show-error",
            "http://127.0.0.1:11434/api/embed",
            "-H",
            "Content-Type: application/json",
            "-d",
            '{"model":"bge-m3:latest","input":"zero-agent stage gate"}',
        )

    new_text = advance_context(text, stage)
    if new_text != text:
        CONTEXT.write_text(new_text, encoding="utf-8")
        print(f"PASS: {stage} gate passed; PROJECT_CONTEXT.md advanced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
