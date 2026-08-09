from pathlib import Path

import pytest

from app.tools.filesystem import FileSystemTool


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "agent.py").write_text("# fake agent")
    (tmp_path / "README.md").write_text("# Zero-Agent")
    return tmp_path


def test_list_root(project_dir: Path) -> None:
    tool = FileSystemTool(root_dir=str(project_dir))
    result = tool.run(action="list", path=".")
    assert "app/" in result
    assert "README.md" in result


def test_list_subdirectory(project_dir: Path) -> None:
    tool = FileSystemTool(root_dir=str(project_dir))
    result = tool.run(action="list", path="app")
    assert "agent.py" in result


def test_read_file(project_dir: Path) -> None:
    tool = FileSystemTool(root_dir=str(project_dir))
    result = tool.run(action="read", path="README.md")
    assert result == "# Zero-Agent"


def test_read_missing_file(project_dir: Path) -> None:
    tool = FileSystemTool(root_dir=str(project_dir))
    result = tool.run(action="read", path="nao_existe.txt")
    assert "não encontrado" in result


def test_path_traversal_is_blocked(project_dir: Path) -> None:
    tool = FileSystemTool(root_dir=str(project_dir))
    with pytest.raises(PermissionError):
        tool.run(action="list", path="../")


def test_unknown_action_raises(project_dir: Path) -> None:
    tool = FileSystemTool(root_dir=str(project_dir))
    with pytest.raises(ValueError):
        tool.run(action="delete", path=".")
