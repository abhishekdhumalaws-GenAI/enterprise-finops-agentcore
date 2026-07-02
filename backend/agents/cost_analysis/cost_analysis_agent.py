from backend.services.cost_summary_service import CostSummaryService
from backend.services.recommendation_service import RecommendationService
from backend.services.tool_registry import ToolRegistry
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class CostAnalysisAgent:
    def __init__(self):
        self.name = "Cost Analysis Agent"
        self.tool_registry = ToolRegistry()
        self.cost_tool = self.tool_registry.get_tool("cost_explorer")
        self.summary_service = CostSummaryService()
        self.recommendation_service = RecommendationService()

    def handle(self, parsed_request):
        service = parsed_request.get("service")
        days = parsed_request.get("days", 7)

        logger.info(f"{self.name} handling request | service={service} | days={days}")

        cost_data = self.cost_tool.get_cost(
            days=days,
            service_filter=service
        )

        if isinstance(cost_data, dict) and cost_data.get("error"):
            return {
                "agent": self.name,
                "service": service or "All AWS Services",
                "days": days,
                "error": cost_data,
                "cost_summary": None,
                "recommendations": [
                    "Unable to fetch AWS cost data. Please check IAM permissions and Cost Explorer availability."
                ],
                "cost_data": []
            }

        cost_summary = self.summary_service.summarize(
            cost_data,
            days=days,
            service=service
        )

        recommendations = self.recommendation_service.get_recommendations(
            service=service,
            total_cost=cost_summary["total_cost"]
        )

        return {
            "agent": self.name,
            "service": service or "All AWS Services",
            "days": days,
            "cost_summary": cost_summary,
            "recommendations": recommendations,
            "cost_data": cost_data
        }

