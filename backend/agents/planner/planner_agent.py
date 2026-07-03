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

        investigation_keywords = [
            "why",
            "increase",
            "spike",
            "anomaly",
            "unusual",
            "root cause",
            "unexpected",
            "sudden"
        ]

        optimization_keywords = [
            "reduce",
            "optimize",
            "optimization",
            "recommend optimization",
            "recommend optimizations",
            "recommend",
            "save",
            "saving",
            "savings",
            "lower cost",
            "cost reduction",
            "aws bill",
            "analyze my aws bill",
            "recommend optimizations"
        ]

        if any(word in query for word in investigation_keywords):
            return {
                "workflow": "cost_investigation",
                "agents": [
                    "organizations",
                    "cost_analysis",
                    "cur",
                    "cost_anomaly_detection",
                    "pricing",
                    "budgets",
                    "ec2_discovery",
                    "cloudwatch"
                ],
                "reason": "User is asking for cost increase, anomaly, or root cause investigation."
            }

        if any(word in query for word in optimization_keywords):
            return {
                "workflow": "optimization",
                "agents": [
                    "organizations",
                    "cost_analysis",
                    "cur",
                    "cost_anomaly_detection",
                    "pricing",
                    "budgets",
                    "ec2_discovery",
                    "cloudwatch",
                    "compute_optimization"
                ],
                "reason": "User is asking for AWS cost optimization and savings recommendations."
            }

        return {
            "workflow": "single_agent",
            "agents": [parsed_request.get("intent", "cost_analysis")],
            "reason": "Default single-agent execution."
        }
