import os
import uuid
import json
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, Any

import boto3


class WorkflowStore:
    def __init__(self):
        self.table_name = os.getenv(
            "WORKFLOW_TABLE_NAME",
            "enterprise-finops-workflows"
        )
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)

    def create_workflow(self, workflow_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = f"workflow-{uuid.uuid4()}"

        item = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "status": "CREATED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "payload": self._to_dynamodb_safe(payload)
        }

        self.table.put_item(Item=item)

        return item

    def _to_dynamodb_safe(self, data):
        return json.loads(
            json.dumps(data),
            parse_float=Decimal
        )

    def list_workflows(self, limit: int = 25) -> Dict[str, Any]:
        response = self.table.scan(
            Limit=limit
        )

        items = response.get("Items", [])

        items = sorted(
            items,
            key=lambda item: item.get("created_at", ""),
            reverse=True
        )

        return {
            "count": len(items),
            "workflows": items
        }

    def update_workflow_status(
        self,
        workflow_id: str,
        status: str,
        details: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:

        self.table.update_item(
            Key={"workflow_id": workflow_id},
            UpdateExpression="SET #status = :status, updated_at = :updated_at, details = :details",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":status": status,
                ":updated_at": datetime.now(timezone.utc).isoformat(),
                ":details": self._to_dynamodb_safe(details or {})
            }
        )

        return {
            "workflow_id": workflow_id,
            "status": status,
            "details": details or {}
        }
