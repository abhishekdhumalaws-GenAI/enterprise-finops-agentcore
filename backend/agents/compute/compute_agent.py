from backend.services.tool_registry import ToolRegistry


class ComputeAgent:
    def __init__(self):
        self.name = "Compute Optimization Agent"
        self.tool_registry = ToolRegistry()
        self.compute_optimizer = self.tool_registry.get_tool("compute_optimizer")

    def handle(self, parsed_request):
        recommendations = self.compute_optimizer.get_ec2_recommendations()

        return {
            "agent": self.name,
            "service": "EC2",
            "optimization_type": "rightsizing",
            "recommendations": recommendations
        }
