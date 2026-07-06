import json
import os
from datetime import datetime, timezone
from typing import Dict, Any

import boto3


class StepFunctionsService:
    def __init__(self):
        self.state_machine_arn = os.getenv("FINOPS_STATE_MACHINE_ARN")
        self.client = boto3.client("stepfunctions")

    def is_enabled(self) -> bool:
        return bool(self.state_machine_arn)

    def start_execution(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.state_machine_arn:
            return {
                "enabled": False,
                "status": "SKIPPED",
                "message": "FINOPS_STATE_MACHINE_ARN is not configured."
            }

        response = self.client.start_execution(
            stateMachineArn=self.state_machine_arn,
            input=json.dumps(payload, default=str)
        )

        return {
            "enabled": True,
            "status": "STARTED",
            "execution_arn": response.get("executionArn"),
            "start_date": response.get("startDate").isoformat()
            if response.get("startDate") else None,
            "started_at": datetime.now(timezone.utc).isoformat()
        }

    def describe_execution(self, execution_arn: str) -> Dict[str, Any]:
        response = self.client.describe_execution(
            executionArn=execution_arn
        )

        return {
            "execution_arn": response.get("executionArn"),
            "state_machine_arn": response.get("stateMachineArn"),
            "name": response.get("name"),
            "status": response.get("status"),
            "start_date": response.get("startDate").isoformat()
            if response.get("startDate") else None,
            "stop_date": response.get("stopDate").isoformat()
            if response.get("stopDate") else None,
            "input": response.get("input"),
            "output": response.get("output")
        }

    def list_executions(self, max_results: int = 10) -> Dict[str, Any]:
        if not self.state_machine_arn:
            return {
                "enabled": False,
                "status": "SKIPPED",
                "message": "FINOPS_STATE_MACHINE_ARN is not configured.",
                "executions": []
            }

        response = self.client.list_executions(
            stateMachineArn=self.state_machine_arn,
            maxResults=max_results
        )

        executions = []

        for execution in response.get("executions", []):
            executions.append({
                "execution_arn": execution.get("executionArn"),
                "state_machine_arn": execution.get("stateMachineArn"),
                "name": execution.get("name"),
                "status": execution.get("status"),
                "start_date": execution.get("startDate").isoformat()
                if execution.get("startDate") else None,
                "stop_date": execution.get("stopDate").isoformat()
                if execution.get("stopDate") else None,
                "redrive_count": execution.get("redriveCount", 0)
            })

        return {
            "enabled": True,
            "status": "SUCCESS",
            "state_machine_arn": self.state_machine_arn,
            "count": len(executions),
            "executions": executions
        }

    def get_execution_metrics(self, max_results: int = 50) -> Dict[str, Any]:
        executions_response = self.list_executions(max_results=max_results)
        executions = executions_response.get("executions", [])

        total = len(executions)
        succeeded = 0
        failed = 0
        running = 0
        timed_out = 0
        aborted = 0
        durations_ms = []

        for execution in executions:
            status = execution.get("status")

            if status == "SUCCEEDED":
                succeeded += 1
            elif status == "FAILED":
                failed += 1
            elif status == "RUNNING":
                running += 1
            elif status == "TIMED_OUT":
                timed_out += 1
            elif status == "ABORTED":
                aborted += 1

            start_date = execution.get("start_date")
            stop_date = execution.get("stop_date")

            if start_date and stop_date:
                from datetime import datetime

                start = datetime.fromisoformat(start_date)
                stop = datetime.fromisoformat(stop_date)
                duration_ms = round((stop - start).total_seconds() * 1000, 2)
                durations_ms.append(duration_ms)

        avg_duration_ms = (
            round(sum(durations_ms) / len(durations_ms), 2)
            if durations_ms else 0
        )

        success_rate = (
            round((succeeded / total) * 100, 2)
            if total else 0
        )

        return {
            "enabled": executions_response.get("enabled", False),
            "state_machine_arn": executions_response.get("state_machine_arn"),
            "total_executions": total,
            "succeeded": succeeded,
            "failed": failed,
            "running": running,
            "timed_out": timed_out,
            "aborted": aborted,
            "success_rate": success_rate,
            "average_duration_ms": avg_duration_ms,
            "executions": executions
        }
