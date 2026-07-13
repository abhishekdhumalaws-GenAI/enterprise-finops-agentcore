from enum import Enum


class ToolName(str, Enum):
    COST_EXPLORER = "cost_explorer"
    COST_ANOMALY = "cost_anomaly"
    PRICING = "pricing"
    BUDGETS = "budgets"
    ORGANIZATIONS = "organizations"
    EC2_DISCOVERY = "ec2_discovery"
    CLOUDWATCH_METRICS = "cloudwatch_metrics"
    COMPUTE_OPTIMIZER = "compute_optimizer"
    CUR = "cur"
