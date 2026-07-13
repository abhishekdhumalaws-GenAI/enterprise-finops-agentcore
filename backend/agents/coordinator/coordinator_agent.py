import time

from backend.agents.planner.planner_agent import PlannerAgent
from backend.agents.reviewer.reviewer_agent import ReviewerAgent
from backend.services.agent_registry import AgentRegistry
from backend.services.llm_service import LLMService
from backend.agents.optimization_planner.optimization_planner_agent import OptimizationPlannerAgent
from backend.engines.decision_engine.ai_decision_engine import AIDecisionEngine
from backend.engines.reasoning_engine.ai_reasoning_engine import AIReasoningEngine
from backend.agents.approval_workflow.approval_workflow_agent import ApprovalWorkflowAgent
from backend.engines.change_manager.enterprise_change_manager import EnterpriseChangeManager
from backend.services.demo.demo_finops_data import get_demo_execution_results
from backend.agents.execution_planner.execution_planner_agent import ExecutionPlannerAgent
from backend.agent_runtime.agent_registry import AgentName
from backend.services.execution_context import ExecutionContext
from backend.agent_runtime.execution_context import ExecutionContext as RuntimeExecutionContext
from backend.agent_runtime.runtime_singleton import agent_runtime


class CoordinatorAgent:
    def __init__(self):
        self.name = "FinOps Coordinator Agent"
        self.planner = PlannerAgent()
        self.registry = AgentRegistry()
        self.llm_service = LLMService()
        self.reviewer = ReviewerAgent()
        self.optimization_planner_agent = OptimizationPlannerAgent()
        self.decision_engine = AIDecisionEngine()
        self.reasoning_engine = AIReasoningEngine()
        self.approval_workflow_agent = ApprovalWorkflowAgent()
        self.change_manager = EnterpriseChangeManager()
        self.execution_planner_agent = ExecutionPlannerAgent()
        self.agent_runtime = agent_runtime

    def _build_runtime_payload(self, execution_results, context, user_query, parsed_request):
        return {
            "user_query": user_query,
            "parsed_request": parsed_request,
            "cost_analysis": execution_results.get("cost_analysis", {}),
            "anomalies": execution_results.get("cost_anomaly_detection", {}).get("anomalies", []),
            "ec2_discovery": execution_results.get("ec2_discovery", {}),
            "cloudwatch_metrics": execution_results.get("cloudwatch", {}),
            "compute_optimization": execution_results.get("compute_optimization", {}),
            "pricing": execution_results.get("pricing", {}),
            "budgets": execution_results.get("budgets", {}),
            "cur": execution_results.get("cur", {}),
            "organizations": execution_results.get("organizations", {}),
            "context": context.to_dict(),
        }

    def _run_runtime_planner_and_decision(self, execution_results, context, user_query, parsed_request):
        runtime_context = RuntimeExecutionContext(
            payload=self._build_runtime_payload(
                execution_results=execution_results,
                context=context,
                user_query=user_query,
                parsed_request=parsed_request,
            )
        )

        planner_execution = self.agent_runtime.invoke_agent(
            AgentName.OPTIMIZATION_PLANNER.value,
            context=runtime_context,
        )

        optimization_plan = planner_execution.get("output") or {
            "agent": "optimization_planner_agent",
            "status": "failed",
            "optimization_summary": {
                "total_opportunities": 0,
                "high_priority": 0,
                "approval_required_count": 0,
                "estimated_monthly_savings_total_usd": 0,
            },
            "optimization_plan": [],
        }

        runtime_context.add_result(
            AgentName.OPTIMIZATION_PLANNER.value,
            optimization_plan,
        )

        runtime_context.payload["optimization_plan"] = optimization_plan

        decision_execution = self.agent_runtime.delegate_agent(
            from_agent=AgentName.OPTIMIZATION_PLANNER.value,
            to_agent=AgentName.DECISION_ENGINE.value,
            context=runtime_context,
            parent_execution_id=planner_execution.get("execution_id"),
            reason=(
                "Evaluate optimization recommendations, calculate decision scores, "
                "and determine approval requirements."
            ),
        )

        decision_result = decision_execution.get("output") or {
            "agent": "Decision Engine Agent",
            "status": "failed",
            "summary": {
                "estimated_monthly_savings_usd": 0,
                "estimated_annual_savings_usd": 0,
            },
            "decisions": [],
        }

        runtime_context.add_result(
            AgentName.DECISION_ENGINE.value,
            decision_result,
        )

        return optimization_plan, decision_result, planner_execution, decision_execution, runtime_context,

    def handle(self, user_query: str, parsed_request: dict):
        start_time = time.time()
        context = ExecutionContext()

        plan = self.planner.create_plan(user_query, parsed_request)

        if not plan or plan.get("workflow") == "single_agent":
            return None

        execution_results = {}
        demo_mode = any(
            word in user_query.lower()
            for word in ["demo mode", "mock data", "sample data"]
        )

        if demo_mode:
            execution_results = get_demo_execution_results()

            (
                optimization_plan,
                decision_result,
                planner_execution,
                decision_execution,
                runtime_context,
            ) = self._run_runtime_planner_and_decision(
                execution_results=execution_results,
                context=context,
                user_query=user_query,
                parsed_request=parsed_request,
            )

            reasoning_result = self.reasoning_engine.generate(decision_result)

            runtime_context.remember(
                key="reasoning_engine",
                value=reasoning_result,
                source="reasoning_engine",
                category="agent_result",
            )

            approval_execution = self.agent_runtime.delegate_agent(
                from_agent=AgentName.DECISION_ENGINE.value,
                to_agent=AgentName.APPROVAL_WORKFLOW.value,
                context=runtime_context,
                parent_execution_id=decision_execution.get("execution_id"),
                reason=(
                    "Create approval requests for recommendations that require "
                    "human authorization based on decision and risk analysis."
                ),
            )

            approval_result = approval_execution.get("output") or {
                "agent": "Approval Runtime Agent",
                "status": "failed",
                "approval_required": False,
                "approval_count": 0,
                "approvals": [],
            }

            runtime_context.add_result(
                AgentName.APPROVAL_WORKFLOW.value,
                approval_result,
            )
            change_result = self.change_manager.create_change_requests(approval_result)

            runtime_context.remember(
                key="change_manager",
                value=change_result,
                source="change_manager",
                category="agent_result",
            )

            execution_planner_execution = self.agent_runtime.delegate_agent(
                from_agent=AgentName.APPROVAL_WORKFLOW.value,
                to_agent=AgentName.EXECUTION_PLANNER.value,
                context=runtime_context,
                parent_execution_id=approval_execution.get("execution_id"),
                reason=(
                    "Execute the approved optimization plan generated by the "
                    "execution planner."
                ),
            )

            execution_plan_result = execution_planner_execution.get("output") or {
                "agent": "Execution Planner Runtime Agent",
                "status": "failed",
                "execution_plans_count": 0,
                "execution_plans": [],
            }

            runtime_context.add_result(
                AgentName.EXECUTION_PLANNER.value,
                execution_plan_result,
            )

            combined_result = {
                "agent": self.name,
                "planner": self.planner.name,
                "plan": {
                    "workflow": "demo_optimization",
                    "agents": plan.get("agents", []),
                    "reason": "Demo mode uses realistic mock FinOps data.",
                },
                "agent_runtime": {
                    "planner_execution": planner_execution,
                    "decision_execution": decision_execution,
                    "approval_execution": approval_execution,
                    "execution_planner_execution": execution_planner_execution,
                },
                "context": context.to_dict(),
                "execution_results": execution_results,
                "optimization_plan": optimization_plan,
                "decision_engine": decision_result,
                "reasoning_engine": reasoning_result,
                "approval_workflow": approval_result,
                "change_manager": change_result,
                "execution_planner": execution_plan_result,
                "demo_mode": True,
            }

            return {
                "coordinated": True,
                "final_answer": (
                    "# Enterprise FinOps Demo Mode\n\n"
                    "Demo mode executed successfully using realistic mock AWS FinOps data.\n\n"
                    "The platform generated optimization plans, decision scores, reasoning, approval requests, and enterprise change requests without consuming Bedrock tokens or live AWS cost data."
                ),
                "result": combined_result,
            }

        for agent_name in plan.get("agents", []):
            agent = self.registry.get_agent(agent_name)

            if not agent:
                execution_results[agent_name] = {
                    "error": f"No agent found for {agent_name}"
                }
                continue

            agent_request = self._build_agent_request(
                agent_name=agent_name,
                parsed_request=parsed_request,
                workflow=plan.get("workflow"),
                user_query=user_query,
                context=context,
            )

            execution_results[agent_name] = agent.handle(agent_request)

            self._update_context_from_result(
                agent_name=agent_name,
                result=execution_results[agent_name],
                context=context,
            )

        (
            optimization_plan,
            decision_result,
            planner_execution,
            decision_execution,
            runtime_context,
        ) = self._run_runtime_planner_and_decision(
            execution_results=execution_results,
            context=context,
            user_query=user_query,
            parsed_request=parsed_request,
        )

        reasoning_result = self.reasoning_engine.generate(decision_result)

        runtime_context.remember(
            key="reasoning_engine",
            value=reasoning_result,
            source="reasoning_engine",
            category="agent_result",
        )

        approval_execution = self.agent_runtime.delegate_agent(
            from_agent=AgentName.DECISION_ENGINE.value,
            to_agent=AgentName.APPROVAL_WORKFLOW.value,
            context=runtime_context,
            parent_execution_id=decision_execution.get("execution_id"),
            reason=(
                "Create approval requests for recommendations that require "
                "human authorization based on decision and risk analysis."
            ),
        )

        approval_result = approval_execution.get("output") or {
            "agent": "Approval Runtime Agent",
            "status": "failed",
            "approval_required": False,
            "approval_count": 0,
            "approvals": [],
        }

        runtime_context.add_result(
            AgentName.APPROVAL_WORKFLOW.value,
            approval_result,
        )

        change_result = self.change_manager.create_change_requests(approval_result)

        runtime_context.remember(
            key="change_manager",
            value=change_result,
            source="change_manager",
            category="agent_result",
        )

        execution_execution = self.agent_runtime.delegate_agent(
            from_agent=AgentName.EXECUTION_PLANNER.value,
            to_agent=AgentName.EXECUTION.value,
            context=runtime_context,
            parent_execution_id=execution_planner_execution.get("execution_id"),
            reason=(
                "Execute the approved optimization plan generated by the "
                "execution planner."
            ),
        )

        execution_plan_result = execution_planner_execution.get("output") or {
            "agent": "Execution Planner Runtime Agent",
            "status": "failed",
            "execution_plans_count": 0,
            "execution_plans": [],
        }

        runtime_context.add_result(
            AgentName.EXECUTION_PLANNER.value,
            execution_plan_result,
        )

        combined_result = {
            "agent": self.name,
            "planner": self.planner.name,
            "plan": plan,
            "agent_runtime": {
                "planner_execution": planner_execution,
                "decision_execution": decision_execution,
                "approval_execution": approval_execution,
                "execution_planner_execution": execution_planner_execution,
            },
            "context": context.to_dict(),
            "execution_results": execution_results,
            "optimization_plan": optimization_plan,
            "decision_engine": decision_result,
            "reasoning_engine": reasoning_result,
            "approval_workflow": approval_result,
            "change_manager": change_result,
            "execution_planner": execution_plan_result,
        }

        structured_response = self.llm_service.generate_structured_finops_answer(
            user_query=user_query,
            parsed_request={
                "intent": "planned_multi_agent_workflow",
                "workflow": plan.get("workflow"),
                "agents": plan.get("agents"),
                "phase": "optimization_planning",
            },
            result=combined_result,
        )

        review = None

        if structured_response.get("success"):
            grounded_facts = structured_response.get("grounded_facts", {})
            review = self.reviewer.review(
                structured_answer=structured_response["answer"],
                grounded_facts=grounded_facts,
            )

            if review.get("approved"):
                final_answer = self.llm_service.format_structured_answer(
                    structured_response["answer"]
                )
            else:
                final_answer = (
                    "# Review Failed\n"
                    "The AI-generated response did not pass grounding validation.\n\n"
                    "Issues:\n"
                    + "\n".join(
                        f"- {issue}" for issue in review.get("issues", [])
                    )
                )
        else:
            final_answer = structured_response.get("fallback_answer")

            if not final_answer:
                final_answer = (
                    "# Enterprise FinOps Analysis Completed\n\n"
                    "The multi-agent FinOps workflow completed successfully, but Amazon Bedrock could not generate the final natural-language summary.\n\n"
                    "Please review the structured result below, including optimization_plan, decision_engine, reasoning_engine, approval_workflow, and change_manager.\n\n"
                    f"Error: {structured_response.get('error', 'Unknown LLM error')}"
                )

        execution_time_ms = round((time.time() - start_time) * 1000, 2)

        metadata = {
            "workflow": plan.get("workflow"),
            "agents_invoked": plan.get("agents", []),
            "phase": "optimization_planning",
            "execution_time_ms": execution_time_ms,
            "aws_tool_calls": self._estimate_aws_tool_calls(plan.get("agents", [])),
            "llm_calls": 1,
            "confidence": self._estimate_confidence(execution_results),
            "review": review,
        }

        combined_result["metadata"] = metadata

        return {
            "coordinated": True,
            "final_answer": final_answer,
            "result": combined_result,
        }

    def _build_agent_request(
        self,
        agent_name: str,
        parsed_request: dict,
        workflow: str,
        user_query: str,
        context: ExecutionContext,
    ):
        days = parsed_request.get("days", 30)
        metric = parsed_request.get("metric", "UnblendedCost")

        if agent_name == "cost_analysis":
            service = parsed_request.get("service")

            if workflow == "cost_investigation":
                service = None

            return {
                "intent": "cost_analysis",
                "service": service,
                "days": days,
                "metric": metric,
            }

        if agent_name == "cost_anomaly_detection":
            return {
                "intent": "cost_anomaly_detection",
                "service": "Cost Anomaly Detection",
                "days": days,
                "metric": metric,
            }

        if agent_name == "compute_optimization":
            return {
                "intent": "compute_optimization",
                "service": "EC2",
                "days": days,
                "metric": metric,
            }

        if agent_name == "pricing":
            instance_type = context.get("instance_type") or "g5.xlarge"

            return {
                "intent": "pricing",
                "service": "EC2",
                "region": "US East (N. Virginia)",
                "instance_type": instance_type,
            }

        if agent_name == "budgets":
            return {
                "intent": "budgets",
                "service": "AWS Budgets",
            }

        if agent_name == "ec2_discovery":
            instance_type = context.get("instance_type") or "g5.xlarge"

            return {
                "intent": "ec2_discovery",
                "service": "Amazon EC2",
                "instance_type": instance_type,
            }

        if agent_name == "cloudwatch":
            return {
                "intent": "cloudwatch",
                "service": "Amazon CloudWatch",
                "namespace": "AWS/EC2",
                "metric_name": "CPUUtilization",
                "dimension_name": "InstanceId",
                "dimension_value": context.get("instance_id"),
                "days": days,
            }

        if agent_name == "organizations":
            return {
                "intent": "organizations",
                "service": "AWS Organizations",
            }

        if agent_name == "cur":
            return {
                "intent": "cur",
                "days": days,
                "metric": metric,
            }

        return parsed_request

    def _extract_instance_type_from_results(self, parsed_request: dict):
        service = parsed_request.get("service")

        if service == "EC2":
            return "g5.xlarge"

        return None

    def _update_context_from_result(
        self,
        agent_name: str,
        result: dict,
        context: ExecutionContext,
    ):
        if agent_name == "cost_anomaly_detection":
            anomalies = result.get("anomalies", [])

            for anomaly in anomalies:
                for cause in anomaly.get("root_causes", []):
                    usage_type = cause.get("UsageType")

                    if usage_type and usage_type.startswith("BoxUsage:"):
                        instance_type = usage_type.split("BoxUsage:")[-1]
                        context.set("instance_type", instance_type)
                        context.add_fact(
                            f"Discovered EC2 instance type from anomaly: {instance_type}"
                        )
                        return

        if agent_name == "ec2_discovery":
            discovery = result.get("ec2_discovery", {})
            data = discovery.get("data", {})
            instances = data.get("instances", [])

            if instances:
                instance = instances[0]
                context.set("instance_id", instance.get("instance_id"))
                context.set("instance_state", instance.get("state"))
                context.add_fact(
                    f"Discovered EC2 instance ID: {instance.get('instance_id')}"
                )
            else:
                context.add_warning(
                    "No EC2 instances found for discovered instance type."
                )

    def _estimate_aws_tool_calls(self, agents):
        count = 0

        for agent in agents:
            if agent in [
                "cost_analysis",
                "cost_anomaly_detection",
                "compute_optimization",
                "governance_optimization",
                "pricing",
                "budgets",
                "ec2_discovery",
                "organizations",
                "cloudwatch",
                "cur",
            ]:
                count += 1

        return count

    def _estimate_confidence(self, execution_results):
        if not execution_results:
            return 0.0

        failures = 0

        for result in execution_results.values():
            if isinstance(result, dict):
                if result.get("error"):
                    failures += 1

                if result.get("success") is False:
                    failures += 1

        confidence = 1 - (failures / len(execution_results))
        return round(confidence, 2)
