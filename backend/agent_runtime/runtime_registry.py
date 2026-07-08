from backend.agent_runtime.runtime import AgentRuntime
from backend.agents.optimization_planner.optimization_planner_agent import OptimizationPlannerAgent
from backend.agents.approval_workflow.approval_workflow_agent import ApprovalWorkflowAgent
from backend.agents.execution_planner.execution_planner_agent import ExecutionPlannerAgent
from backend.agents.execution.execution_agent import ExecutionAgent
from backend.agents.verification.verification_agent import VerificationAgent
from backend.agents.rollback.rollback_agent import RollbackAgent
from backend.agent_runtime.agent_registry import AgentName

def build_agent_runtime() -> AgentRuntime:
    runtime = AgentRuntime()

    runtime.register_agent(
        AgentName.OPTIMIZATION_PLANNER.value,
        OptimizationPlannerAgent()
    )

    runtime.register_agent(
        AgentName.APPROVAL_WORKFLOW.value,
        ApprovalWorkflowAgent()
    )

    runtime.register_agent(
        AgentName.EXECUTION_PLANNER.value,
        ExecutionPlannerAgent()
    )

    runtime.register_agent(
        AgentName.EXECUTION.value,
        ExecutionAgent()
    )

    runtime.register_agent(
        AgentName.VERIFICATION.value,
        VerificationAgent()
    )

    runtime.register_agent(
        AgentName.ROLLBACK.value,
        RollbackAgent()
    )

    return runtime
