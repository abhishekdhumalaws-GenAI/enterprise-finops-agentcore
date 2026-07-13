from fastapi import Depends, FastAPI
from pydantic import BaseModel
from backend.agents.coordinator.coordinator_agent import CoordinatorAgent
from fastapi import Depends
from backend.services.auth.cognito_auth import get_current_user, require_groups

from typing import Dict, Any
from backend.agents.execution.execution_agent import ExecutionAgent
from backend.config.settings import settings
from backend.services.request_parser import RequestParser
from backend.services.agent_registry import AgentRegistry
from backend.services.response_formatter import ResponseFormatter
from backend.services.llm_service import LLMService
from backend.orchestrators.stepfunctions_simulator import StepFunctionsSimulator
from backend.services.workflow_store.workflow_store import WorkflowStore
from backend.services.stepfunctions.stepfunctions_service import StepFunctionsService
from backend.services.metrics.cloudwatch_metrics import CloudWatchMetrics
from backend.agent_runtime.runtime_singleton import agent_runtime
from backend.agent_runtime.agent_registry import AgentName
from backend.agent_runtime.execution_context import ExecutionContext as RuntimeExecutionContext
from backend.tool_runtime.tool_bootstrap import bootstrap_tools
from backend.tool_runtime.tool_registry_singleton import tool_registry
from backend.tool_runtime.tool_orchestrator_singleton import tool_orchestrator
from backend.formatter_runtime.formatter_bootstrap import bootstrap_formatters
from backend.formatter_runtime.formatter_registry_singleton import formatter_registry

app = FastAPI(title=settings.APP_NAME)

parser = RequestParser()
registry = AgentRegistry()
formatter = ResponseFormatter()
llm_service = LLMService()
coordinator = CoordinatorAgent()
execution_agent = ExecutionAgent()
stepfunctions_simulator = StepFunctionsSimulator()
workflow_store = WorkflowStore()
stepfunctions_service = StepFunctionsService()
cloudwatch_metrics = CloudWatchMetrics()
bootstrap_tools()

class FinOpsRequest(BaseModel):
    user_query: str

class ExecuteRequest(BaseModel):
    execution_plan: Dict[str, Any]
    approved: bool = False

class AgentRuntimeRequest(BaseModel):
    agent_name: str
    payload: Dict[str, Any]

class ToolInvocationRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}

class ToolOrchestrationRequest(BaseModel):
    intent: str
    service: str | None = None
    arguments: Dict[str, Any] = {}

@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": settings.APP_NAME
    }


@app.post("/analyze")
def analyze(request: FinOpsRequest, current_user: dict = Depends(get_current_user)
):
    parsed_request = parser.parse(request.user_query)
    coordinated_response = coordinator.handle(request.user_query, parsed_request)
    result_for_storage = coordinated_response.get("result") if coordinated_response else None

    if result_for_storage and isinstance(result_for_storage, dict):
        result_for_storage = result_for_storage.copy()

        agent_runtime = result_for_storage.get("agent_runtime", {})

        if agent_runtime:
            result_for_storage["agent_runtime"] = {
                key: {
                    "execution_id": value.get("execution_id"),
                    "workflow_id": value.get("workflow_id"),
                    "parent_execution_id": value.get("parent_execution_id"),
                    "agent_name": value.get("agent_name"),
                    "status": value.get("status"),
                    "duration_ms": value.get("duration_ms"),
                }
                for key, value in agent_runtime.items()
                if isinstance(value, dict)
            }
    workflow_payload = {
        "user_query": request.user_query,
        "parsed_request": parsed_request,
        "coordinated": bool(coordinated_response),
        "final_answer": coordinated_response.get("final_answer") if coordinated_response else None,
        "result": result_for_storage
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

        try:
            execution_result = coordinated_response.get("result", {})
            cloudwatch_metrics.publish_analysis_metrics(execution_result)
        except Exception as error:
            logger.warning(f"CloudWatch metrics publish failed: {error}")

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
        formatter_result = formatter_registry.format(
            intent=parsed_request["intent"],
            result=result,
        )

        if formatter_result.get("status") == "succeeded":
            final_answer = formatter_result["formatted_response"]

        else:
            final_answer = (
                "Request completed, but no formatter is available "
                f"for intent '{parsed_request['intent']}'."
            )

    return {
        "user_query": request.user_query,
        "parsed_request": parsed_request,
        "final_answer": final_answer,
        "result": result,
        "message": "Request parsed and handled by Agent Registry."
    }

@app.post("/execute")
def execute_change(request: ExecuteRequest,
    current_user: dict = Depends(get_current_user)
):
    require_groups(
        current_user,
        ["Approver", "Admin"]
    )

    runtime_context = RuntimeExecutionContext(
        payload={
            "execution_plan": request.execution_plan,
            "approved": request.approved,
            "user": current_user
        }
    )

    execution_runtime_record = agent_runtime.invoke_agent(
        AgentName.EXECUTION.value,
        context=runtime_context
    )

    result = execution_runtime_record.get("output") or {
        "agent": "Execution Runtime Agent",
        "status": "failed",
        "error": "Execution runtime failed."
    }

    runtime_context.payload["execution_result"] = result

    verification_runtime_record = agent_runtime.delegate_agent(
        from_agent=AgentName.EXECUTION.value,
        to_agent=AgentName.VERIFICATION.value,
        context=runtime_context,
        parent_execution_id=execution_runtime_record.get("execution_id"),
        reason=(
            "Verify the approved FinOps execution result and determine "
            "whether rollback is required."
        ),
    )

    verification_result = verification_runtime_record.get("output") or {
        "agent": "Verification Runtime Agent",
        "status": "failed",
        "overall_result": "FAILED",
        "checks": [],
        "summary": {
            "checks_passed": 0,
            "checks_failed": 1,
            "rollback_required": True
        }
    }

    result["verification"] = verification_result

    runtime_context.payload["verification_result"] = verification_result

    rollback_runtime_record = None
    rollback_result = None

    rollback_required = (
        verification_result
        .get("summary", {})
        .get("rollback_required", False)
    )

    if rollback_required:
        rollback_runtime_record = agent_runtime.delegate_agent(
            from_agent=AgentName.VERIFICATION.value,
            to_agent=AgentName.ROLLBACK.value,
            context=runtime_context,
            parent_execution_id=verification_runtime_record.get("execution_id"),
            reason=(
                "Verification identified an unsuccessful or unsafe change, "
                "so restore the previous configuration."
            ),
        )

        rollback_result = rollback_runtime_record.get("output") or {
            "agent": "Rollback Runtime Agent",
            "status": "failed",
            "rollback_required": True,
            "error": "Rollback runtime failed."
        }

        result["rollback"] = rollback_result
    else:
        result["rollback"] = {
            "agent": "Rollback Runtime Agent",
            "status": "skipped",
            "rollback_required": False,
            "message": "Verification passed. Rollback not required."
        }

    orchestration = stepfunctions_simulator.run(result)
    stepfunctions_execution = stepfunctions_service.start_execution({
        "execution_result": result,
        "orchestration": orchestration
    })

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
            "orchestration": orchestration,
            "stepfunctions_execution": stepfunctions_execution
        }
    )

    try:
        cloudwatch_metrics.publish_execution_metrics(result)
    except Exception as error:
        logger.warning(f"CloudWatch execution metrics failed: {error}")


    return {
        "workflow_id": workflow_record["workflow_id"],
        "execution_requested": True,
        "approved": request.approved,
        "result": result,
        "orchestration": orchestration,
        "stepfunctions_execution": stepfunctions_execution,
        "agent_runtime": {
            "execution_runtime_record": execution_runtime_record,
            "verification_runtime_record": verification_runtime_record,
            "rollback_runtime_record": rollback_runtime_record
        }
    }

@app.get("/workflows")
def list_workflows(current_user: dict = Depends(get_current_user)
):
    return workflow_store.list_workflows()

@app.get("/stepfunctions/status")
def get_stepfunctions_status(execution_arn: str, current_user: dict = Depends(get_current_user)
):
    status = stepfunctions_service.describe_execution(execution_arn)

    return {
        "execution_arn": execution_arn,
        "status": status
    }

@app.get("/stepfunctions/executions")
def list_stepfunctions_executions(max_results: int = 10, current_user: dict = Depends(get_current_user)
):
    executions = stepfunctions_service.list_executions(max_results=max_results)

    return executions

@app.get("/stepfunctions/metrics")
def get_stepfunctions_metrics(max_results: int = 50, current_user: dict = Depends(get_current_user)
):
    metrics = stepfunctions_service.get_execution_metrics(max_results=max_results)

    return metrics

@app.get("/agent-runtime/agents")
def list_runtime_agents(
    current_user: dict = Depends(get_current_user)
):
    return {
        "count": len(agent_runtime.list_agents()),
        "agents": agent_runtime.list_agents()
    }


@app.post("/agent-runtime/invoke")
def invoke_runtime_agent(
    request: AgentRuntimeRequest,
    current_user: dict = Depends(get_current_user)
):
    require_groups(
        current_user,
        ["Admin"]
    )

    return agent_runtime.invoke_agent(
        request.agent_name,
        request.payload
    )

@app.get("/agent-runtime/executions")
def list_runtime_executions(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    require_groups(
        current_user,
        ["Admin"]
    )

    return {
        "count": len(agent_runtime.list_executions(limit=limit)),
        "executions": agent_runtime.list_executions(limit=limit)
    }

@app.get("/agent-runtime/workflows/{workflow_id}/executions")
def list_runtime_workflow_executions(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    require_groups(
        current_user,
        ["Admin"]
    )

    executions = agent_runtime.list_workflow_executions(workflow_id)

    return {
        "workflow_id": workflow_id,
        "count": len(executions),
        "executions": executions
    }

@app.get("/tool-runtime/tools")
def list_runtime_tools(
    current_user: dict = Depends(get_current_user)
):
    require_groups(
        current_user,
        ["Admin"]
    )

    tools = tool_registry.list_tools()

    return {
        "count": len(tools),
        "tools": tools,
    }

@app.post("/tool-runtime/invoke")
def invoke_runtime_tool(
    request: ToolInvocationRequest,
    current_user: dict = Depends(get_current_user)
):
    require_groups(
        current_user,
        ["Admin"]
    )

    return tool_registry.invoke_tool(
        request.tool_name,
        **request.arguments
    )

@app.post("/tool-runtime/orchestrate")
def orchestrate_runtime_tool(
    request: ToolOrchestrationRequest,
    current_user: dict = Depends(get_current_user),
):
    require_groups(
        current_user,
        ["Admin"],
    )

    return tool_orchestrator.orchestrate(
        intent=request.intent,
        service=request.service,
        arguments=request.arguments,
    )
