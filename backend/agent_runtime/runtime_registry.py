from backend.agent_runtime.runtime import AgentRuntime
from backend.agents.optimization_planner.optimization_planner_agent import OptimizationPlannerAgent
from backend.agents.approval_workflow.approval_workflow_agent import ApprovalWorkflowAgent
from backend.agents.execution_planner.execution_planner_agent import ExecutionPlannerAgent
from backend.agents.execution.execution_agent import ExecutionAgent
from backend.agents.verification.verification_agent import VerificationAgent
from backend.agents.rollback.rollback_agent import RollbackAgent
from backend.agent_runtime.agent_registry import AgentName
from backend.agents.decision_engine.decision_engine_agent import DecisionEngineAgent
from backend.agents.runtime_approval.approval_runtime_agent import ApprovalRuntimeAgent
from backend.agents.runtime_execution_planner.execution_planner_runtime_agent import ExecutionPlannerRuntimeAgent
from backend.agents.runtime_execution.execution_runtime_agent import ExecutionRuntimeAgent
from backend.agents.runtime_verification.verification_runtime_agent import VerificationRuntimeAgent
from backend.agents.runtime_rollback.rollback_runtime_agent import RollbackRuntimeAgent

def build_agent_runtime() -> AgentRuntime:
    runtime = AgentRuntime()

    runtime.register_agent(
        AgentName.OPTIMIZATION_PLANNER.value,
        OptimizationPlannerAgent()
    )

    runtime.register_agent(
        AgentName.APPROVAL_WORKFLOW.value,
        ApprovalRuntimeAgent()
    )

    runtime.register_agent(
        AgentName.EXECUTION_PLANNER.value,
        ExecutionPlannerRuntimeAgent()
    )

    runtime.register_agent(
        AgentName.EXECUTION.value,
        ExecutionRuntimeAgent()
    )

    runtime.register_agent(
        AgentName.VERIFICATION.value,
        VerificationRuntimeAgent()
    )

    runtime.register_agent(
        AgentName.ROLLBACK.value,
        RollbackRuntimeAgent()
    )

    runtime.register_agent(
        AgentName.DECISION_ENGINE.value,
        DecisionEngineAgent()
    )

    return runtime
