from typing import Dict, Set, Any

class Clients:
    """Manages downstream WebSocket clients and fan-out by refId."""
    def __init__(self) -> None:
        self._all: Set[Any] = set()
        self._by_ref: Dict[str, Set[Any]] = {}

    def add_all(self, ws: Any) -> None:
        self._all.add(ws)

    def remove_all(self, ws: Any) -> None:
        self._all.discard(ws)

    def add_ref(self, ref_id: str, ws: Any) -> None:
        self._by_ref.setdefault(ref_id, set()).add(ws)

    def remove_ref(self, ref_id: str, ws: Any) -> None:
        s = self._by_ref.get(ref_id)
        if s:
            s.discard(ws)
            if not s:
                self._by_ref.pop(ref_id, None)

    def push_all(self, payload: str) -> None:
        dead = []
        for ws in list(self._all):
            try:
                ws.send(payload)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.remove_all(d)

    def push_ref(self, ref_id: str, payload: str) -> None:
        dead = []
        for ws in list(self._by_ref.get(ref_id, ())):
            try:
                ws.send(payload)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.remove_ref(ref_id, d)

# export a singleton registry
clients = Clients()
