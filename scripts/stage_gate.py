#!/usr/bin/env python3
"""Run the acceptance gate for the documented milestone."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "PROJECT_CONTEXT.md"
SUPPORTED_GATES = {"v0.1", "v0.2", "v0.3", "v0.4", "v0.5"}
ORDER = ["v0.1", "v0.2", "v0.3", "v0.4", "v0.5", "v0.6", "v0.7", "v0.8", "v0.9", "v1.0"]


def run(*args: str) -> None:
    print("$", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def current_stage(text: str) -> str:
    match = re.search(r"^v(\d+\.\d+): IN PROGRESS$", text, re.MULTILINE)
    if match:
        return f"v{match.group(1)}"
    raise RuntimeError("No IN PROGRESS milestone found in PROJECT_CONTEXT.md")


def advance_context(text: str, stage: str) -> str:
    index = ORDER.index(stage)
    if index + 1 >= len(ORDER):
        return text

    next_stage = ORDER[index + 1]

    # The next run must have exactly one detectable IN PROGRESS milestone.
    # The previous implementation changed the next milestone to NEXT, which
    # made the following invocation fail with "No IN PROGRESS milestone".
    text = re.sub(
        rf"^{re.escape(stage)}: IN PROGRESS$",
        f"{stage}: DONE",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text = re.sub(
        rf"^NEXT MILESTONE: {re.escape(stage)}$",
        f"NEXT MILESTONE: {next_stage}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text = re.sub(
        rf"^{re.escape(next_stage)}: (?:TODO|NEXT|IN PROGRESS)$",
        f"{next_stage}: IN PROGRESS",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text = re.sub(
        rf"({re.escape(stage)}[^\n]*\[)IN PROGRESS(\])",
        r"\1DONE\2",
        text,
        count=1,
    )
    text = re.sub(
        rf"({re.escape(next_stage)}[^\n]*\[)(?:TODO|NEXT|IN PROGRESS)(\])",
        r"\1IN PROGRESS\2",
        text,
        count=1,
    )
    return text


def main() -> int:
    text = CONTEXT.read_text(encoding="utf-8")
    stage = current_stage(text)
    print(f"Detected milestone: {stage}")

    if stage not in SUPPORTED_GATES:
        print(f"BLOCKED: no explicit automatic acceptance gate is defined for {stage}.")
        print("Add the stage's real acceptance checks before allowing automatic promotion.")
        return 2

    run(sys.executable, "-m", "pytest", "-v")

    if stage == "v0.3":
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

    if stage == "v0.4":
        run(sys.executable, "-m", "pytest", "-v", "tests/test_rag.py")

    if stage == "v0.5":
        # Planning is accepted only when both the planner contract and the
        # real multi-step executor are covered by the automated suite.
        run(sys.executable, "-m", "pytest", "-v", "tests/test_planner.py", "tests/test_executor.py")

    new_text = advance_context(text, stage)
    if new_text != text:
        CONTEXT.write_text(new_text, encoding="utf-8")
        print(f"PASS: {stage} gate passed; PROJECT_CONTEXT.md advanced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
