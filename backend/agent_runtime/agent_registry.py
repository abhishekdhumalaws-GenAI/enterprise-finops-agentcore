from enum import Enum


class AgentName(str, Enum):
    COST_ANALYSIS = "cost_analysis"
    OPTIMIZATION_PLANNER = "optimization_planner"
    DECISION_ENGINE = "decision_engine"
    APPROVAL_WORKFLOW = "approval_workflow"
    EXECUTION_PLANNER = "execution_planner"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    ROLLBACK = "rollback"
