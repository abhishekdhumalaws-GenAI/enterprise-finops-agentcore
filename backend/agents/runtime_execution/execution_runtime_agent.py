from backend.agents.execution.execution_agent import ExecutionAgent


class ExecutionRuntimeAgent:
    def __init__(self):
        self.name = "Execution Runtime Agent"
        self.execution_agent = ExecutionAgent()

    def handle_request(self, request: dict):
        execution_plan = request.get("execution_plan")
        approved = request.get("approved", False)

        if not execution_plan:
            return {
                "agent": self.name,
                "status": "failed",
                "error": "Missing execution_plan in runtime payload."
            }

        return self.execution_agent.execute(
            execution_plan=execution_plan,
            approved=approved
        )
