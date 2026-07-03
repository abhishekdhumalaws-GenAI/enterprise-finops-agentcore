from datetime import datetime, timezone


class StepFunctionsSimulator:
    def __init__(self):
        self.name = "Step Functions Simulator"

    def run(self, execution_result):
        rollback_required = (
            execution_result
            .get("verification", {})
            .get("summary", {})
            .get("rollback_required", False)
        )

        workflow_events = [
            {
                "state": "PreCheck",
                "status": "PASSED",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "state": "ExecuteChange",
                "status": execution_result.get("status"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "state": "VerifyChange",
                "status": execution_result.get("verification", {}).get("overall_result"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "state": "RollbackDecision",
                "rollback_required": rollback_required,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]

        if rollback_required:
            workflow_events.append({
                "state": "PrepareRollback",
                "status": "READY",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            final_state = "CompleteWithRollback"
        else:
            final_state = "Complete"

        workflow_events.append({
            "state": final_state,
            "status": "SUCCEEDED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        return {
            "orchestrator": self.name,
            "status": "SUCCEEDED",
            "workflow": "finops_execution_workflow",
            "final_state": final_state,
            "events": workflow_events
        }
