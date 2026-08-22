from pathlib import Path

import pytest

from scripts import stage_gate


def test_current_stage_requires_exactly_one_in_progress() -> None:
    text = "v0.5: IN PROGRESS\nv0.6: IN PROGRESS\n"
    with pytest.raises(RuntimeError, match="exactly one"):
        stage_gate.current_stage(text)


def test_validate_stage_context_requires_next_milestone() -> None:
    text = "v0.5: IN PROGRESS\nNEXT MILESTONE: v0.7\n"
    with pytest.raises(RuntimeError, match="NEXT MILESTONE"):
        stage_gate.validate_stage_context(text, "v0.5")


def test_advance_context_marks_current_done_and_next_in_progress() -> None:
    text = "v0.5: IN PROGRESS\nNEXT MILESTONE: v0.5\nv0.6: TODO\n"
    updated = stage_gate.advance_context(text, "v0.5")

    assert "v0.5: DONE" in updated
    assert "NEXT MILESTONE: v0.6" in updated
    assert "v0.6: IN PROGRESS" in updated


def test_stage_gate_does_not_write_when_promotion_disabled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    context = tmp_path / "PROJECT_CONTEXT.md"
    original = "v0.5: IN PROGRESS\nNEXT MILESTONE: v0.6\n"
    context.write_text(original, encoding="utf-8")

    monkeypatch.setattr(stage_gate, "CONTEXT", context)
    monkeypatch.setenv("PROMOTE_STAGE", "false")
    monkeypatch.setattr(stage_gate, "run", lambda *args: None)

    assert stage_gate.main() == 0
    assert context.read_text(encoding="utf-8") == original
