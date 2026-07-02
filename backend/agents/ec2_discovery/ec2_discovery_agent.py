from backend.services.tool_registry import ToolRegistry


class EC2DiscoveryAgent:
    def __init__(self):
        self.name = "EC2 Discovery Agent"
        self.tool_registry = ToolRegistry()

    def handle(self, request: dict):
        instance_type = request.get("instance_type")

        discovery_tool = self.tool_registry.get_tool("ec2_discovery")

        result = discovery_tool.execute(
            instance_type=instance_type
        )

        return {
            "agent": self.name,
            "service": "Amazon EC2",
            "discovery_type": "instances",
            "instance_type": instance_type,
            "ec2_discovery": result
        }
