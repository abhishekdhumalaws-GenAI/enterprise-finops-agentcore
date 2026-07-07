from backend.agent_runtime.runtime import AgentRuntime
from backend.agents.optimization_planner.optimization_planner_agent import OptimizationPlannerAgent
from backend.agents.approval_workflow.approval_workflow_agent import ApprovalWorkflowAgent
from backend.agents.execution_planner.execution_planner_agent import ExecutionPlannerAgent
from backend.agents.execution.execution_agent import ExecutionAgent
from backend.agents.verification.verification_agent import VerificationAgent
from backend.agents.rollback.rollback_agent import RollbackAgent


def build_agent_runtime() -> AgentRuntime:
    runtime = AgentRuntime()

    runtime.register_agent(
        "optimization_planner",
        OptimizationPlannerAgent()
    )

    runtime.register_agent(
        "approval_workflow",
        ApprovalWorkflowAgent()
    )

    runtime.register_agent(
        "execution_planner",
        ExecutionPlannerAgent()
    )

    runtime.register_agent(
        "execution",
        ExecutionAgent()
    )

    runtime.register_agent(
        "verification",
        VerificationAgent()
    )

    runtime.register_agent(
        "rollback",
        RollbackAgent()
    )

    return runtime
