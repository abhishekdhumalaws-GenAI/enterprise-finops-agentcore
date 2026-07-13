from typing import Any, Dict, Optional

from backend.tool_runtime.tool_names import ToolName
from backend.tool_runtime.tool_registry_singleton import tool_registry


class ToolOrchestrator:
    def __init__(self):
        self.registry = tool_registry

    def select_tool(
        self,
        intent: str,
        service: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_intent = (intent or "").strip().lower()
        normalized_service = (service or "").strip().lower()

        if normalized_intent in {
            "cost_analysis",
            "cost",
            "cost_explorer",
            "aws_cost",
        }:
            return {
                "tool_name": ToolName.COST_EXPLORER.value,
                "reason": "Cost analysis requires AWS Cost Explorer data.",
            }

        if normalized_intent in {
            "cost_anomaly_detection",
            "cost_anomaly",
            "anomaly",
        }:
            return {
                "tool_name": ToolName.COST_ANOMALY.value,
                "reason": "Cost anomaly analysis requires Cost Anomaly Detection data.",
            }

        if normalized_intent in {
            "pricing",
            "price_lookup",
            "ec2_pricing",
        }:
            return {
                "tool_name": ToolName.PRICING.value,
                "reason": "Pricing intent requires the AWS Pricing tool.",
            }

        if normalized_intent in {
            "budgets",
            "budget",
            "budget_analysis",
        }:
            return {
                "tool_name": ToolName.BUDGETS.value,
                "reason": "Budget analysis requires AWS Budgets data.",
            }

        if normalized_intent in {
            "organizations",
            "accounts",
            "multi_account",
        }:
            return {
                "tool_name": ToolName.ORGANIZATIONS.value,
                "reason": "Account discovery requires AWS Organizations.",
            }

        if normalized_intent in {
            "ec2_discovery",
            "instance_discovery",
            "discover_instances",
        }:
            return {
                "tool_name": ToolName.EC2_DISCOVERY.value,
                "reason": "EC2 discovery requires the EC2 Discovery tool.",
            }

        if normalized_intent in {
            "cloudwatch",
            "cloudwatch_metrics",
            "metrics",
            "utilization",
        }:
            return {
                "tool_name": ToolName.CLOUDWATCH_METRICS.value,
                "reason": "Metric analysis requires CloudWatch data.",
            }

        if normalized_intent in {
            "compute_optimization",
            "compute_optimizer",
            "rightsizing",
        }:
            return {
                "tool_name": ToolName.COMPUTE_OPTIMIZER.value,
                "reason": "Rightsizing requires Compute Optimizer recommendations.",
            }

        if normalized_intent in {
            "cur",
            "cost_usage_report",
            "cost_and_usage_report",
        }:
            return {
                "tool_name": ToolName.CUR.value,
                "reason": "Detailed billing analysis requires Cost and Usage Reports.",
            }

        if normalized_service in {"ec2", "amazon ec2"}:
            return {
                "tool_name": ToolName.EC2_DISCOVERY.value,
                "reason": "EC2 service context matched the EC2 Discovery tool.",
            }

        return {
            "tool_name": None,
            "reason": f"No registered tool mapping found for intent '{intent}'.",
        }

    def orchestrate(
        self,
        intent: str,
        arguments: Optional[Dict[str, Any]] = None,
        service: Optional[str] = None,
    ) -> Dict[str, Any]:
        selection = self.select_tool(
            intent=intent,
            service=service,
        )

        tool_name = selection.get("tool_name")

        if not tool_name:
            return {
                "status": "failed",
                "intent": intent,
                "selected_tool": None,
                "selection_reason": selection.get("reason"),
                "error": "No suitable registered tool was found.",
            }

        invocation = self.registry.invoke_tool(
            tool_name,
            **(arguments or {}),
        )

        return {
            "status": invocation.get("status"),
            "intent": intent,
            "selected_tool": tool_name,
            "selection_reason": selection.get("reason"),
            "arguments": arguments or {},
            "tool_result": invocation.get("result"),
            "error": invocation.get("error"),
        }
