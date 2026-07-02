from backend.services.tool_registry import ToolRegistry


class BudgetsAgent:
    def __init__(self):
        self.name = "Budgets Agent"
        self.tool_registry = ToolRegistry()

    def handle(self, request: dict):
        budgets_tool = self.tool_registry.get_tool("budgets")
        result = budgets_tool.execute()

        return {
            "agent": self.name,
            "service": "AWS Budgets",
            "budgets": result
        }
