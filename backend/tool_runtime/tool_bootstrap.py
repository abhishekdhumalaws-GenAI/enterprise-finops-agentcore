from backend.tool_runtime.tool_names import ToolName
from backend.tool_runtime.tool_registry_singleton import tool_registry

from backend.tools.cost_explorer_tool import CostExplorerTool
from backend.tools.cost_anomaly_tool import CostAnomalyTool
from backend.tools.pricing_tool import PricingTool
from backend.tools.budgets_tool import BudgetsTool
from backend.tools.organizations_tool import OrganizationsTool
from backend.tools.ec2_discovery_tool import EC2DiscoveryTool
from backend.tools.cloudwatch_tool import CloudWatchTool
from backend.tools.compute_optimizer_tool import ComputeOptimizerTool
from backend.tools.cur_tool import CURTool


def bootstrap_tools():
    if tool_registry.list_tools():
        return tool_registry

    cost_explorer = CostExplorerTool()
    cost_anomaly = CostAnomalyTool()
    pricing = PricingTool()
    budgets = BudgetsTool()
    organizations = OrganizationsTool()
    ec2_discovery = EC2DiscoveryTool()
    cloudwatch = CloudWatchTool()
    compute_optimizer = ComputeOptimizerTool()
    cur = CURTool()

    tool_registry.register_tool(
        name=ToolName.COST_EXPLORER.value,
        handler=cost_explorer.get_cost,
        description="Fetch AWS cost and usage data.",
        category="finops",
    )

    tool_registry.register_tool(
        name=ToolName.COST_ANOMALY.value,
        handler=cost_anomaly.execute,
        description="Fetch AWS cost anomalies.",
        category="finops",
    )

    tool_registry.register_tool(
        name=ToolName.PRICING.value,
        handler=pricing.execute,
        description="Fetch EC2 On-Demand pricing.",
        category="pricing",
    )

    tool_registry.register_tool(
        name=ToolName.BUDGETS.value,
        handler=budgets.execute,
        description="List AWS Budgets.",
        category="governance",
    )

    tool_registry.register_tool(
        name=ToolName.ORGANIZATIONS.value,
        handler=organizations.execute,
        description="List AWS Organizations accounts.",
        category="governance",
    )

    tool_registry.register_tool(
        name=ToolName.EC2_DISCOVERY.value,
        handler=ec2_discovery.execute,
        description="Discover EC2 instances.",
        category="compute",
    )

    tool_registry.register_tool(
        name=ToolName.CLOUDWATCH_METRICS.value,
        handler=cloudwatch.execute,
        description="Fetch CloudWatch metrics.",
        category="observability",
    )

    tool_registry.register_tool(
        name=ToolName.COMPUTE_OPTIMIZER.value,
        handler=compute_optimizer.get_ec2_recommendations,
        description="Fetch Compute Optimizer recommendations.",
        category="optimization",
    )

    tool_registry.register_tool(
        name=ToolName.CUR.value,
        handler=cur.execute,
        description="List Cost and Usage Reports.",
        category="finops",
    )

    return tool_registry
