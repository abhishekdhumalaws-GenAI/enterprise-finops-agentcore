from backend.services.tool_registry import ToolRegistry


class OrganizationsAgent:
    def __init__(self):
        self.name = "Organizations Agent"
        self.tool_registry = ToolRegistry()

    def handle(self, request: dict):
        organizations_tool = self.tool_registry.get_tool("organizations")

        result = organizations_tool.execute()

        return {
            "agent": self.name,
            "service": "AWS Organizations",
            "organizations": result
        }
