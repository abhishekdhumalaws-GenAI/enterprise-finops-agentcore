import time

from backend.agents.planner.planner_agent import PlannerAgent
from backend.agents.reviewer.reviewer_agent import ReviewerAgent
from backend.services.agent_registry import AgentRegistry
from backend.services.llm_service import LLMService
from backend.services.execution_context import ExecutionContext

class CoordinatorAgent:
    def __init__(self):
        self.name = "FinOps Coordinator Agent"
        self.planner = PlannerAgent()
        self.registry = AgentRegistry()
        self.llm_service = LLMService()
        self.reviewer = ReviewerAgent()

    def handle(self, user_query: str, parsed_request: dict):
        start_time = time.time()
        context = ExecutionContext()

        plan = self.planner.create_plan(user_query, parsed_request)

        if not plan or plan.get("workflow") == "single_agent":
            return None

        execution_results = {}

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
                context=context
            )

            execution_results[agent_name] = agent.handle(agent_request)

        self._update_context_from_result(
            agent_name=agent_name,
            result=execution_results[agent_name],
            context=context
        )

        combined_result = {
            "agent": self.name,
            "planner": self.planner.name,
            "plan": plan,
            "execution_results": context.to_dict(),
            "execution_results": execution_results
        }

        structured_response = self.llm_service.generate_structured_finops_answer(
            user_query=user_query,
            parsed_request={
                "intent": "planned_multi_agent_workflow",
                "workflow": plan.get("workflow"),
                "agents": plan.get("agents")
            },
            result=combined_result
        )

        review = None

        if structured_response.get("success"):
            grounded_facts = structured_response.get("grounded_facts", {})
            review = self.reviewer.review(
                structured_answer=structured_response["answer"],
                grounded_facts=grounded_facts
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
            final_answer = structured_response.get(
                "fallback_answer",
                "Unable to generate FinOps response."
            )

        execution_time_ms = round((time.time() - start_time) * 1000, 2)

        metadata = {
            "workflow": plan.get("workflow"),
            "agents_invoked": plan.get("agents", []),
            "execution_time_ms": execution_time_ms,
            "aws_tool_calls": self._estimate_aws_tool_calls(plan.get("agents", [])),
            "llm_calls": 1,
            "confidence": self._estimate_confidence(execution_results),
            "review": review
        }

        combined_result["metadata"] = metadata

        return {
            "coordinated": True,
            "final_answer": final_answer,
            "result": combined_result
        }

    def _build_agent_request(
        self,
        agent_name: str,
        parsed_request: dict,
        workflow: str,
        user_query: str,
        context: ExecutionContext
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
                "metric": metric
            }

        if agent_name == "cost_anomaly_detection":
            return {
                "intent": "cost_anomaly_detection",
                "service": "Cost Anomaly Detection",
                "days": days,
                "metric": metric
            }

        if agent_name == "compute_optimization":
            return {
                "intent": "compute_optimization",
                "service": "EC2",
                "days": days,
                "metric": metric
            }

        if agent_name == "pricing":
            instance_type = context.get("instance_type") or "g5.xlarge"

            return {
                "intent": "pricing",
                "service": "EC2",
                "region": "US East (N. Virginia)",
                "instance_type": instance_type
            }

        if agent_name == "budgets":
            return {
                "intent": "budgets",
                "service": "AWS Budgets"
            }

        if agent_name == "ec2_discovery":
            instance_type = context.get("instance_type") or "g5.xlarge"

            return {
                "intent": "ec2_discovery",
                "service": "Amazon EC2",
                "instance_type": instance_type
            }

        if agent_name == "cloudwatch":
            return {
                "intent": "cloudwatch",
                "service": "Amazon CloudWatch",
                "namespace": "AWS/EC2",
                "metric_name": "CPUUtilization",
                "dimension_name": "InstanceId",
                "dimension_value": context.get("instance_id"),
                "days": days
            }

        return parsed_request

    def _extract_instance_type_from_results(self, parsed_request: dict):
        service = parsed_request.get("service")

        if service == "EC2":
            return "g5.xlarge"

        return None

    def _update_context_from_result(self, agent_name: str, result: dict, context: ExecutionContext):
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
                "ec2_discovery"
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
