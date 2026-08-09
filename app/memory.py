"""
Stub da interface de memória.

Sem lógica real ainda. A implementação (SQLite, tabela `experiences`
conforme o roadmap) chega no v0.5. Esta interface existe apenas para que
outros módulos já possam depender de IMemory por tipo, sem acoplamento
a uma implementação concreta, evitando retrabalho quando o v0.5 chegar.
"""
from __future__ import annotations

from typing import Any, Protocol


class IMemory(Protocol):
    def save(self, key: str, value: Any) -> None: ...

    def load(self, key: str) -> Any: ...
