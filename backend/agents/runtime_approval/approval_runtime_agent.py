from backend.agents.approval_workflow.approval_workflow_agent import (
    ApprovalWorkflowAgent,
)
from backend.agent_runtime.execution_context import ExecutionContext


class ApprovalRuntimeAgent:
    def __init__(self):
        self.name = "Approval Runtime Agent"
        self.approval_agent = ApprovalWorkflowAgent()

    def handle_context(self, context: ExecutionContext):
        reasoning_result = context.recall("reasoning_engine")

        if not reasoning_result:
            return {
                "agent": self.name,
                "status": "failed",
                "approval_required": False,
                "approval_count": 0,
                "approvals": [],
                "error": "Missing reasoning_engine result in workflow memory.",
            }

        return self.approval_agent.create_approval_requests(
            reasoning_result
        )
