from backend.agents.ec2_discovery.ec2_discovery_agent import EC2DiscoveryAgent
from backend.agents.cloudwatch.cloudwatch_agent import CloudWatchAgent
from backend.agents.cost_analysis.cost_analysis_agent import CostAnalysisAgent
from backend.agents.compute.compute_agent import ComputeAgent
from backend.agents.governance.governance_agent import GovernanceAgent
from backend.agents.anomaly.anomaly_agent import AnomalyDetectionAgent
from backend.agents.pricing.pricing_agent import PricingAgent
from backend.agents.budgets.budgets_agent import BudgetsAgent
from backend.agents.cur.cur_agent import CURAgent
from backend.agents.organizations.organizations_agent import OrganizationsAgent
from backend.agents.optimization_planner.optimization_planner_agent import OptimizationPlannerAgent
from backend.agents.approval_workflow.approval_workflow_agent import ApprovalWorkflowAgent
from backend.agents.execution_planner.execution_planner_agent import ExecutionPlannerAgent

class AgentRegistry:
    def __init__(self):
        self.agents = {
            "cost_analysis": CostAnalysisAgent(),
            "compute_optimization": ComputeAgent(),
            "governance_optimization": GovernanceAgent(),
            "cost_anomaly_detection": AnomalyDetectionAgent(),
            "pricing": PricingAgent(),
            "budgets": BudgetsAgent(),
            "cloudwatch": CloudWatchAgent(),
            "ec2_discovery": EC2DiscoveryAgent(),
            "cur": CURAgent(),
            "organizations": OrganizationsAgent(),
            "optimization_planner": OptimizationPlannerAgent(),
            "approval_workflow": ApprovalWorkflowAgent(),
            "execution_planner": ExecutionPlannerAgent(),
        }

    def get_agent(self, intent: str):
        return self.agents.get(intent)
