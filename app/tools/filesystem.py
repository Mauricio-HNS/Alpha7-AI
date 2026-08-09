"""
FileSystemTool.

Escopo do v0.1: apenas listar e ler arquivos, restrito a um diretório raiz
(sem escapar via '..' ou caminhos absolutos). Escrita de arquivos fica para
um próximo incremento, quando houver um caso de uso real que a exija -
adicionar agora seria antecipar requisito não solicitado pelo milestone
atual (listar arquivos do projeto).
"""
from __future__ import annotations

from pathlib import Path


class FileSystemTool:
    name = "filesystem"
    description = (
        'Lista ou lê arquivos dentro do diretório raiz permitido. '
        'Parâmetros: action ("list" ou "read"), path (relativo ao diretório raiz, padrão ".").'
    )

    def __init__(self, root_dir: str = ".") -> None:
        self.root_dir = Path(root_dir).resolve()

    def run(self, action: str, path: str = ".") -> str:
        if action == "list":
            return self._list(path)
        if action == "read":
            return self._read(path)
        raise ValueError(f"Ação desconhecida para FileSystemTool: {action!r}")

    def _resolve(self, path: str) -> Path:
        target = (self.root_dir / path).resolve()
        if self.root_dir not in target.parents and target != self.root_dir:
            raise PermissionError(f"Acesso negado: '{path}' está fora do diretório raiz permitido.")
        return target

    def _list(self, path: str) -> str:
        target = self._resolve(path)
        if not target.exists():
            return f"Caminho não encontrado: {path}"
        if not target.is_dir():
            return f"Não é um diretório: {path}"
        entries = sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())
        return "\n".join(entries) if entries else "(diretório vazio)"

    def _read(self, path: str) -> str:
        target = self._resolve(path)
        if not target.exists() or not target.is_file():
            return f"Arquivo não encontrado: {path}"
        return target.read_text(encoding="utf-8", errors="replace")
