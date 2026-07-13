from backend.services.cost_summary_service import CostSummaryService
from backend.services.recommendation_service import RecommendationService
from backend.tool_runtime.tool_orchestrator_singleton import tool_orchestrator
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class CostAnalysisAgent:
    def __init__(self):
        self.name = "Cost Analysis Agent"
        self.tool_orchestrator = tool_orchestrator
        self.summary_service = CostSummaryService()
        self.recommendation_service = RecommendationService()

    def handle(self, parsed_request):
        service = parsed_request.get("service")
        days = parsed_request.get("days", 7)

        service_filter = service

        if service_filter in {
            None,
            "",
            "All AWS Services",
            "all",
        }:
            service_filter = None

        logger.info(
            "%s handling request | service=%s | days=%s",
            self.name,
            service_filter,
            days,
        )

        orchestration_result = self.tool_orchestrator.orchestrate(
            intent="cost_analysis",
            service=service_filter,
            arguments={
                "days": days,
                "service_filter": service_filter,
            },
        )

        if orchestration_result.get("status") != "succeeded":
            error = orchestration_result.get(
                "error",
                "Cost Explorer invocation failed.",
            )

            logger.error(
                "Cost Analysis tool orchestration failed | error=%s",
                error,
            )

            return {
                "agent": self.name,
                "success": False,
                "service": service_filter or "All AWS Services",
                "days": days,
                "cost_summary": {
                    "total_cost": 0,
                    "currency": "USD",
                    "top_services": [],
                    "daily_totals": [],
                    "recommendation": "Unable to retrieve AWS cost data.",
                },
                "recommendations": [],
                "cost_data": [],
                "tool_runtime": {
                    "selected_tool": orchestration_result.get("selected_tool"),
                    "selection_reason": orchestration_result.get(
                        "selection_reason"
                    ),
                    "status": orchestration_result.get("status"),
                    "error": error,
                },
            }

        cost_data = orchestration_result.get("tool_result") or []

        if isinstance(cost_data, dict) and cost_data.get("error"):
            return {
                "agent": self.name,
                "success": False,
                "service": service_filter or "All AWS Services",
                "days": days,
                "error": cost_data,
                "cost_summary": None,
                "recommendations": [
                    "Unable to fetch AWS cost data. Please check IAM permissions and Cost Explorer availability."
                ],
                "cost_data": [],
                "tool_runtime": {
                    "selected_tool": orchestration_result.get("selected_tool"),
                    "selection_reason": orchestration_result.get(
                        "selection_reason"
                    ),
                    "status": orchestration_result.get("status"),
                    "error": cost_data,
                },
            }

        cost_summary = self.summary_service.summarize(
            cost_data,
            days=days,
            service=service_filter,
        )

        recommendations = self.recommendation_service.get_recommendations(
            service=service_filter,
            total_cost=cost_summary["total_cost"],
        )

        return {
            "agent": self.name,
            "success": True,
            "service": service_filter or "All AWS Services",
            "days": days,
            "cost_summary": cost_summary,
            "recommendations": recommendations,
            "cost_data": cost_data,
            "tool_runtime": {
                "selected_tool": orchestration_result.get("selected_tool"),
                "selection_reason": orchestration_result.get(
                    "selection_reason"
                ),
                "status": orchestration_result.get("status"),
                "error": orchestration_result.get("error"),
            },
        }
