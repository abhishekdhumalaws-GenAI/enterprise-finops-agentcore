from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents.coordinator.coordinator_agent import CoordinatorAgent

from backend.config.settings import settings
from backend.services.request_parser import RequestParser
from backend.services.agent_registry import AgentRegistry
from backend.services.response_formatter import ResponseFormatter
from backend.services.llm_service import LLMService

app = FastAPI(title=settings.APP_NAME)

parser = RequestParser()
registry = AgentRegistry()
formatter = ResponseFormatter()
llm_service = LLMService()
coordinator = CoordinatorAgent()


class FinOpsRequest(BaseModel):
    user_query: str


@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": settings.APP_NAME
    }


@app.post("/analyze")
def analyze(request: FinOpsRequest):
    parsed_request = parser.parse(request.user_query)
    coordinated_response = coordinator.handle(request.user_query, parsed_request)

    if coordinated_response:
        return {
            "user_query": request.user_query,
            "parsed_request": parsed_request,
            "final_answer": coordinated_response["final_answer"],
            "result": coordinated_response["result"],
            "message": "Request handled by FinOps Coordinator Agent."
        }

    agent = registry.get_agent(parsed_request["intent"])

    if not agent:
        return {
            "user_query": request.user_query,
            "parsed_request": parsed_request,
            "final_answer": "No suitable agent found for this request.",
            "result": None,
            "message": "Agent Registry could not find a matching agent."
        }

    result = agent.handle(parsed_request)

    if parsed_request["intent"] == "cost_analysis":
        final_answer = llm_service.generate_finops_answer(
            user_query=request.user_query,
            parsed_request=parsed_request,
            result=result
        )

        if final_answer.startswith("LLM generation failed"):
            final_answer = formatter.format(result)

    elif parsed_request["intent"] == "compute_optimization":
        recommendations = result.get("recommendations", [])

        if isinstance(recommendations, dict) and recommendations.get("error"):
            final_answer = (
                "EC2 Rightsizing Analysis\n"
                "Unable to fetch Compute Optimizer recommendations.\n"
                "Please verify Compute Optimizer is enabled and IAM permissions are configured."
            )
        else:
            final_answer = (
                "EC2 Rightsizing Analysis\n"
                f"Agent: {result.get('agent')}\n"
                f"Service: {result.get('service')}\n"
                f"Optimization Type: {result.get('optimization_type')}\n"
                f"Recommendations Found: {len(recommendations)}"
            )

    elif parsed_request["intent"] == "governance_optimization":
        checks = result.get("checks", [])

        if isinstance(checks, dict) and checks.get("error"):
            final_answer = (
                "Trusted Advisor Cost Optimization Analysis\n"
                "Unable to fetch Trusted Advisor checks.\n"
                "This usually requires AWS Support API access. "
                "Please verify your AWS Support plan and IAM permissions."
            )
        else:
            flagged_count = 0

            for check in checks:
                summary = check.get("resources_summary", {})
                flagged_count += int(summary.get("resourcesFlagged", 0) or 0)

            final_answer = (
                "Trusted Advisor Cost Optimization Analysis\n"
                f"Agent: {result.get('agent')}\n"
                f"Checks Reviewed: {len(checks)}\n"
                f"Flagged Resources: {flagged_count}\n"
                "Review flagged resources for cost optimization opportunities."
            )

    elif parsed_request["intent"] == "cost_anomaly_detection":
        anomalies = result.get("anomalies", [])

        if not result.get("success"):
            final_answer = (
                "Cost Anomaly Detection Analysis\n"
                "Unable to fetch cost anomalies.\n"
                f"Error: {result.get('error', {}).get('message')}"
            )
        else:
            final_answer = (
                "Cost Anomaly Detection Analysis\n"
                f"Agent: {result.get('agent')}\n"
                f"Anomalies Found: {len(anomalies)}\n"
                "Review anomaly details to identify unexpected AWS spend patterns."
            )

    else:
        final_answer = "Request completed, but no formatter is available for this intent."

    return {
        "user_query": request.user_query,
        "parsed_request": parsed_request,
        "final_answer": final_answer,
        "result": result,
        "message": "Request parsed and handled by Agent Registry."
    }
