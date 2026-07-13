from backend.agents.execution_planner.execution_planner_agent import (
    ExecutionPlannerAgent,
)
from backend.agent_runtime.execution_context import ExecutionContext


class ExecutionPlannerRuntimeAgent:
    def __init__(self):
        self.name = "Execution Planner Runtime Agent"
        self.execution_planner = ExecutionPlannerAgent()

    def handle_context(self, context: ExecutionContext):
        change_result = context.recall("change_manager")

        if not change_result:
            return {
                "agent": self.name,
                "status": "failed",
                "execution_plans_count": 0,
                "execution_plans": [],
                "error": "Missing change_manager result in workflow memory.",
            }

        return self.execution_planner.create_execution_plans(
            change_result
        )
