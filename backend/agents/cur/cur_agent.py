from backend.services.tool_registry import ToolRegistry


class CURAgent:
    def __init__(self):
        self.name = "Cost and Usage Report Agent"
        self.cur_tool = ToolRegistry().get_tool("cur")

    def handle(self, request: dict):
        result = self.cur_tool.execute()

        return {
            "agent": self.name,
            "service": "AWS CUR",
            "cur": result
        }

