from backend.core.base_agent import BaseAgent
from backend.services.tool_registry import ToolRegistry


class AnomalyDetectionAgent(BaseAgent):
    name = "Anomaly Detection Agent"

    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.anomaly_tool = self.tool_registry.get_tool("cost_anomaly")

    def handle(self, parsed_request):
        days = parsed_request.get("days", 30)

        result = self.anomaly_tool.execute(days)

        if not result["success"]:
            return {
                "agent": self.name,
                "success": False,
                "error": result["error"],
                "anomalies": []
            }

        return {
            "agent": self.name,
            "success": True,
            "anomalies": result["data"]
        }
