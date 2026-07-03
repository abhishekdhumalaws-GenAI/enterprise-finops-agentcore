from datetime import datetime, timezone


class RollbackAgent:

    def __init__(self):
        self.name = "Rollback Agent"

    def prepare(self, execution_result):

        rollback_steps = execution_result.get("rollback_steps", [])

        return {
            "agent": self.name,
            "status": "READY",
            "rollback_required": True,
            "rollback_id": f"rollback-{execution_result.get('execution_id')}",
            "prepared_at": datetime.now(timezone.utc).isoformat(),
            "steps": rollback_steps,
            "estimated_duration": "5-15 minutes",
            "approval_required": True
        }

    def execute(self, rollback_plan):

        executed_steps = []

        for step in rollback_plan.get("steps", []):

            executed_steps.append({
                "step": step,
                "status": "SIMULATED_SUCCESS",
                "message": "Rollback simulated successfully."
            })

        return {
            "agent": self.name,
            "status": "ROLLBACK_COMPLETED",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "executed_steps": executed_steps
        }
