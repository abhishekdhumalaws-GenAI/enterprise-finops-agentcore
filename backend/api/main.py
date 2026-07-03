from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents.coordinator.coordinator_agent import CoordinatorAgent

from typing import Dict, Any
from backend.agents.execution.execution_agent import ExecutionAgent
from backend.config.settings import settings
from backend.services.request_parser import RequestParser
from backend.services.agent_registry import AgentRegistry
from backend.services.response_formatter import ResponseFormatter
from backend.services.llm_service import LLMService
from backend.orchestrators.stepfunctions_simulator import StepFunctionsSimulator
from backend.services.workflow_store.workflow_store import WorkflowStore

app = FastAPI(title=settings.APP_NAME)

parser = RequestParser()
registry = AgentRegistry()
formatter = ResponseFormatter()
llm_service = LLMService()
coordinator = CoordinatorAgent()
execution_agent = ExecutionAgent()
stepfunctions_simulator = StepFunctionsSimulator()
workflow_store = WorkflowStore()

class FinOpsRequest(BaseModel):
    user_query: str

class ExecuteRequest(BaseModel):
    execution_plan: Dict[str, Any]
    approved: bool = False

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
    workflow_payload = {
        "user_query": request.user_query,
        "parsed_request": parsed_request,
        "coordinated": bool(coordinated_response),
        "final_answer": coordinated_response.get("final_answer") if coordinated_response else None,
        "result": coordinated_response.get("result") if coordinated_response else None
    }

    workflow_record = workflow_store.create_workflow(
        workflow_type="FINOPS_ANALYSIS",
        payload=workflow_payload
    )

    if coordinated_response:
        workflow_store.update_workflow_status(
            workflow_id=workflow_record["workflow_id"],
            status="PENDING_APPROVAL"
            if coordinated_response.get("result", {}).get("approval_workflow", {}).get("approval_required")
            else "COMPLETED",
            details={
                "approval_workflow": coordinated_response.get("result", {}).get("approval_workflow"),
                "change_manager": coordinated_response.get("result", {}).get("change_manager"),
                "execution_planner": coordinated_response.get("result", {}).get("execution_planner")
            }
        )

        return {
            "workflow_id": workflow_record["workflow_id"],
            "user_query": request.user_query,
            "parsed_request": parsed_request,
            "final_answer": coordinated_response["final_answer"],
            "result": coordinated_response["result"],
            "message": "Request handled by FinOps Coordinator Agent."
        }

    agent = registry.get_agent(parsed_request["intent"])

    if not agent:
        return {
            "workflow_id": workflow_record["workflow_id"],
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

@app.post("/execute")
def execute_change(request: ExecuteRequest):
    result = execution_agent.execute(
        execution_plan=request.execution_plan,
        approved=request.approved
    )

    orchestration = stepfunctions_simulator.run(result)

    workflow_record = workflow_store.create_workflow(
        workflow_type="FINOPS_EXECUTION",
        payload={
            "approved": request.approved,
            "execution_id": result.get("execution_id"),
            "change_id": result.get("change_id"),
            "status": result.get("status"),
            "service": result.get("service"),
            "category": result.get("category")
        }
    )

    workflow_store.update_workflow_status(
        workflow_id=workflow_record["workflow_id"],
        status=result.get("status", "UNKNOWN"),
        details={
            "execution_result": result,
            "orchestration": orchestration
        }
    )

    return {
        "workflow_id": workflow_record["workflow_id"],
        "execution_requested": True,
        "approved": request.approved,
        "result": result,
        "orchestration": orchestration
    }

@app.get("/workflows")
def list_workflows():
    return workflow_store.list_workflows()
