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
