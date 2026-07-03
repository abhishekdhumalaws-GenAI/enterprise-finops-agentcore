from datetime import datetime, timezone
from typing import Dict, Any, List


class ApprovalWorkflowAgent:
    def __init__(self):
        self.name = "Approval Workflow Agent"

    def create_approval_requests(self, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        reasoning_items = reasoning_result.get("reasoning", [])

        approval_requests = []

        for item in reasoning_items:
            approval_path = item.get("approval_path", {})

            if not approval_path.get("approval_required"):
                continue

            approval_requests.append({
                "approval_id": self._approval_id(item),
                "status": "PENDING_APPROVAL",
                "service": item.get("service"),
                "category": item.get("category"),
                "action": item.get("action"),
                "approver": approval_path.get("approver"),
                "approval_reason": approval_path.get("reason"),
                "hypothesis": item.get("hypothesis"),
                "financial_impact": item.get("financial_impact"),
                "risk_assessment": item.get("risk_assessment"),
                "confidence": item.get("confidence"),
                "execution_plan": item.get("execution_plan"),
                "rollback_plan": item.get("rollback_plan"),
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        return {
            "agent": self.name,
            "status": "success",
            "approval_required": len(approval_requests) > 0,
            "approval_count": len(approval_requests),
            "approval_requests": approval_requests
        }

    def _approval_id(self, item: Dict[str, Any]) -> str:
        raw = f"{item.get('category')}-{item.get('service')}-{item.get('action')}"
        cleaned = (
            raw.lower()
            .replace(" ", "-")
            .replace("/", "-")
            .replace(":", "-")
            .replace("_", "-")
        )
        return f"approval-{cleaned[:80]}"
