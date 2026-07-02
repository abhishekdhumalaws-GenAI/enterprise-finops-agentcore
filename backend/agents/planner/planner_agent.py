import json

from backend.services.llm_service import LLMService
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PlannerAgent:
    def __init__(self):
        self.name = "FinOps Planner Agent"
        self.llm_service = LLMService()

    def create_plan(self, user_query: str, parsed_request: dict):
        query = user_query.lower()

        # Safe fallback planning rules
        if any(word in query for word in ["why", "increase", "spike", "anomaly", "unusual"]):
            return {
                "workflow": "cost_investigation",
                "agents": ["cost_analysis", "cur", "cost_anomaly_detection", "pricing", "budgets", "ec2_discovery", "cloudwatch"],
                "reason": "User is asking for cost increase or anomaly investigation."
            }

        if any(word in query for word in ["reduce", "optimize", "save", "saving", "lower cost"]):
            agents = ["cost_analysis", "cur", "cost_anomaly_detection", "pricing", "budgets", "ec2_discovery", "cloudwatch"]

            if parsed_request.get("service") == "EC2" or "ec2" in query:
                agents.append("compute_optimization")

            return {
                "workflow": "optimization",
                "agents": agents,
                "reason": "User is asking for cost optimization."
            }

        return {
            "workflow": "single_agent",
            "agents": [parsed_request.get("intent", "cost_analysis")],
            "reason": "Default single-agent execution."
        }
