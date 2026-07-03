from backend.tools.ec2_discovery_tool import EC2DiscoveryTool
from backend.tools.cloudwatch_tool import CloudWatchTool
from backend.tools.budgets_tool import BudgetsTool
from backend.tools.cost_explorer_tool import CostExplorerTool
from backend.tools.compute_optimizer_tool import ComputeOptimizerTool
from backend.tools.trusted_advisor_tool import TrustedAdvisorTool
from backend.tools.cost_anomaly_tool import CostAnomalyTool
from backend.tools.pricing_tool import PricingTool
from backend.tools.cur_tool import CURTool
from backend.tools.organizations_tool import OrganizationsTool


class ToolRegistry:
    def __init__(self):
        self.tools = {
            "cost_explorer": CostExplorerTool(),
            "compute_optimizer": ComputeOptimizerTool(),
            "trusted_advisor": TrustedAdvisorTool(),
            "cost_anomaly": CostAnomalyTool(),
            "pricing": PricingTool(),
            "budgets": BudgetsTool(),
            "cloudwatch": CloudWatchTool(),
            "ec2_discovery": EC2DiscoveryTool(),
            "cur": CURTool(),
            "organizations": OrganizationsTool(),
        }

    def get_tool(self, tool_name: str):
        return self.tools.get(tool_name)
