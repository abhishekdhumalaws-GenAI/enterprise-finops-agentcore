from datetime import datetime, timezone
from typing import Dict, Any, List
from backend.agents.verification.verification_agent import VerificationAgent
from backend.agents.rollback.rollback_agent import RollbackAgent

class ExecutionAgent:
    def __init__(self):
        self.name = "Execution Agent"
        self.verification_agent = VerificationAgent()
        self.rollback_agent = RollbackAgent()

    def execute(self, execution_plan: Dict[str, Any], approved: bool = False) -> Dict[str, Any]:
        if not approved:
            return {
                "agent": self.name,
                "status": "blocked",
                "message": "Execution blocked because approval was not provided.",
                "execution_id": execution_plan.get("execution_id"),
                "executed_at": datetime.now(timezone.utc).isoformat()
            }

        if execution_plan.get("execution_mode") != "DRY_RUN_ONLY":
            return {
                "agent": self.name,
                "status": "blocked",
                "message": "Only DRY_RUN_ONLY execution mode is currently supported.",
                "execution_id": execution_plan.get("execution_id"),
                "executed_at": datetime.now(timezone.utc).isoformat()
            }

        executed_steps = []

        for step in execution_plan.get("execution_steps", []):
            executed_steps.append({
                "step": step.get("step"),
                "type": step.get("type"),
                "description": step.get("description"),
                "aws_action": step.get("aws_action"),
                "dry_run": True,
                "status": "SIMULATED_SUCCESS",
                "message": "Dry-run simulation completed. No AWS resource was modified."
            })

        execution_result = {
            "agent": self.name,
            "status": "success",
            "execution_mode": "DRY_RUN_ONLY",
            "execution_id": execution_plan.get("execution_id"),
            "change_id": execution_plan.get("change_id"),
            "service": execution_plan.get("service"),
            "category": execution_plan.get("category"),
            "executed_steps": executed_steps,
            "validation_required": True,
            "rollback_available": bool(execution_plan.get("rollback_steps")),
            "executed_at": datetime.now(timezone.utc).isoformat()
        }

        verification = self.verification_agent.verify(
            execution_result
        )

        execution_result["verification"] = verification

        if verification["summary"]["rollback_required"]:

            rollback_plan = self.rollback_agent.prepare(
                {
                    **execution_result,
                    "rollback_steps": execution_plan.get("rollback_steps", [])
                }
            )

            execution_result["rollback"] = rollback_plan

        return execution_result
