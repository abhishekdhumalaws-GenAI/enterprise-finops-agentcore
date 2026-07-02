from backend.services.tool_registry import ToolRegistry


class CloudWatchAgent:
    def __init__(self):
        self.name = "CloudWatch Agent"
        self.tool_registry = ToolRegistry()

    def handle(self, request: dict):
        namespace = request.get("namespace") or "AWS/EC2"
        metric_name = request.get("metric_name") or "CPUUtilization"
        dimension_name = request.get("dimension_name") or "InstanceId"
        dimension_value = request.get("dimension_value")
        days = request.get("days", 7)

        cloudwatch_tool = self.tool_registry.get_tool("cloudwatch")

        result = cloudwatch_tool.execute(
            namespace=namespace,
            metric_name=metric_name,
            dimension_name=dimension_name,
            dimension_value=dimension_value,
            days=days
        )

        return {
            "agent": self.name,
            "service": "Amazon CloudWatch",
            "metric": metric_name,
            "cloudwatch": result
        }
