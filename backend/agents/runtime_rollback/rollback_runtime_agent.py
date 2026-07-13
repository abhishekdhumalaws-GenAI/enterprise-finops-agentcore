from backend.agents.rollback.rollback_agent import RollbackAgent


class RollbackRuntimeAgent:
    def __init__(self):
        self.name = "Rollback Runtime Agent"
        self.rollback_agent = RollbackAgent()

    def handle_request(self, request: dict):
        execution_result = request.get("execution_result")
        verification_result = request.get("verification_result")

        if not execution_result:
            return {
                "agent": self.name,
                "status": "skipped",
                "rollback_required": False,
                "message": "Missing execution_result. Rollback skipped."
            }

        if not verification_result:
            return {
                "agent": self.name,
                "status": "skipped",
                "rollback_required": False,
                "message": "Missing verification_result. Rollback skipped."
            }

        rollback_required = (
            verification_result
            .get("summary", {})
            .get("rollback_required", False)
        )

        if not rollback_required:
            return {
                "agent": self.name,
                "status": "skipped",
                "rollback_required": False,
                "message": "Verification passed. Rollback not required."
            }

        return self.rollback_agent.rollback(
            execution_result=execution_result,
            verification_result=verification_result
        )
