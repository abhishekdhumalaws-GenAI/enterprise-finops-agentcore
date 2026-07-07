import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ExecutionContext:
    def __init__(
        self,
        workflow_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        user: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ):
        self.workflow_id = workflow_id or f"workflow-{uuid.uuid4()}"
        self.correlation_id = correlation_id or f"corr-{uuid.uuid4()}"
        self.user = user or {}
        self.payload = payload or {}

        self.results: Dict[str, Any] = {}
        self.facts: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.errors: List[Dict[str, Any]] = []

        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at

    def add_result(self, key: str, value: Any):
        self.results[key] = value
        self.touch()

    def get_result(self, key: str, default: Any = None):
        return self.results.get(key, default)

    def add_fact(self, fact: Dict[str, Any]):
        self.facts.append(fact)
        self.touch()

    def add_warning(self, warning: str):
        self.warnings.append(warning)
        self.touch()

    def add_error(self, source: str, error: str):
        self.errors.append({
            "source": source,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.touch()

    def touch(self):
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "correlation_id": self.correlation_id,
            "user": self.user,
            "payload": self.payload,
            "results": self.results,
            "facts": self.facts,
            "warnings": self.warnings,
            "errors": self.errors,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        context = cls(
            workflow_id=data.get("workflow_id"),
            correlation_id=data.get("correlation_id"),
            user=data.get("user"),
            payload=data.get("payload"),
        )

        context.results = data.get("results", {})
        context.facts = data.get("facts", [])
        context.warnings = data.get("warnings", [])
        context.errors = data.get("errors", [])
        context.created_at = data.get("created_at", context.created_at)
        context.updated_at = data.get("updated_at", context.updated_at)

        return context
