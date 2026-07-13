from backend.agents.verification.verification_agent import VerificationAgent


class VerificationRuntimeAgent:
    def __init__(self):
        self.name = "Verification Runtime Agent"
        self.verification_agent = VerificationAgent()

    def handle_request(self, request: dict):
        execution_result = request.get("execution_result")

        if not execution_result:
            return {
                "agent": self.name,
                "status": "failed",
                "overall_result": "FAILED",
                "checks": [],
                "summary": {
                    "checks_passed": 0,
                    "checks_failed": 1,
                    "rollback_required": True
                },
                "error": "Missing execution_result in runtime payload."
            }

        return self.verification_agent.verify(execution_result)
