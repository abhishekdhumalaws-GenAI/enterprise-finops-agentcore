from backend.services.tool_registry import ToolRegistry


class GovernanceAgent:
    def __init__(self):
        self.name = "Governance Optimization Agent"
        self.tool_registry = ToolRegistry()
        self.trusted_advisor = self.tool_registry.get_tool("trusted_advisor")

    def handle(self, parsed_request):
        checks = self.trusted_advisor.get_cost_optimization_checks()

        return {
            "agent": self.name,
            "service": "Trusted Advisor",
            "optimization_type": "cost_optimization_checks",
            "checks": checks
        }
