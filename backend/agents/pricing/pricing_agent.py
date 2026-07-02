from backend.services.tool_registry import ToolRegistry


class PricingAgent:
    def __init__(self):
        self.name = "Pricing Agent"
        self.tool_registry = ToolRegistry()

    def handle(self, request: dict):
        service = request.get("service") or "EC2"
        region = request.get("region") or "US East (N. Virginia)"
        instance_type = request.get("instance_type") or "g5.xlarge"

        pricing_tool = self.tool_registry.get_tool("pricing")

        result = pricing_tool.execute(
            service=service,
            region_name=region,
            instance_type=instance_type
        )

        return {
            "agent": self.name,
            "service": service,
            "pricing": result
        }
