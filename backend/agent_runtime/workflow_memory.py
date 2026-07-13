from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class WorkflowMemory:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []

    def put(
        self,
        key: str,
        value: Any,
        source: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.entries.append({
            "key": key,
            "value": value,
            "source": source,
            "category": category,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    def get(self, key: str, default: Any = None):
        for entry in reversed(self.entries):
            if entry.get("key") == key:
                return entry.get("value")

        return default

    def get_by_category(self, category: str):
        return [
            entry
            for entry in self.entries
            if entry.get("category") == category
        ]

    def latest(self, limit: int = 10):
        return self.entries[-limit:]

    def to_dict(self):
        return {
            "entries": self.entries,
            "count": len(self.entries),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        memory = cls()
        memory.entries = data.get("entries", [])
        return memory
