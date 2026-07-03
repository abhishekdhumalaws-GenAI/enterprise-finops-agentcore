import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class OptimizationPlannerAgent:
    def __init__(self):
        self.agent_name = "optimization_planner_agent"

    def handle_request(self, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Optimization Planner Agent started")

        anomalies = context.get("anomalies", [])
        pricing = context.get("pricing", {})
        budgets = context.get("budgets", {})
        ec2_discovery = context.get("ec2_discovery", {})
        cloudwatch = context.get("cloudwatch_metrics", {})
        compute_optimization = context.get("compute_optimization", {})
        cost_analysis = context.get("cost_analysis", {})

        opportunities = []

        opportunities.extend(self._plan_from_anomalies(anomalies, pricing))
        opportunities.extend(self._plan_from_budgets(budgets))
        opportunities.extend(self._plan_from_compute_optimizer(compute_optimization))
        opportunities.extend(self._plan_from_ec2_discovery(ec2_discovery, cloudwatch))
        opportunities.extend(self._plan_from_top_services(cost_analysis))

        ranked_plan = self._rank(opportunities)

        return {
            "agent": self.agent_name,
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "optimization_summary": {
                "total_opportunities": len(ranked_plan),
                "high_priority": len([p for p in ranked_plan if p["priority_score"] >= 80]),
                "approval_required_count": len([p for p in ranked_plan if p["requires_approval"]]),
                "estimated_monthly_savings_total_usd": round(
                    sum(p.get("estimated_monthly_savings_usd", 0) for p in ranked_plan),
                    2
                ),
                "top_recommendation": ranked_plan[0] if ranked_plan else None
            },
            "optimization_plan": ranked_plan,
            "approval_required": any(p["requires_approval"] for p in ranked_plan),
            "next_agent": "reviewer_agent"
        }

    def _plan_from_anomalies(self, anomalies: List[Dict[str, Any]], pricing: Dict[str, Any]):
        plans = []

        price_data = pricing.get("pricing", {}).get("data", {})
        instance_type = price_data.get("instance_type")
        hourly_price = price_data.get("price_per_hour_usd")

        for anomaly in anomalies:
            service = anomaly.get("dimension_value") or "Unknown Service"
            impact = float(anomaly.get("total_impact") or 0)
            percentage = anomaly.get("percentage_impact")
            root_causes = anomaly.get("root_causes", [])

            usage_types = [
                cause.get("UsageType")
                for cause in root_causes
                if cause.get("UsageType")
            ]

            if "Elastic Compute Cloud" in service:
                monthly_projection = round(hourly_price * 730, 2) if hourly_price else round(impact * 30, 2)

                plans.append({
                    "category": "EC2",
                    "action": "Investigate and optimize GPU EC2 usage",
                    "service": service,
                    "resource_hint": instance_type or self._extract_instance_type(usage_types),
                    "evidence": {
                        "anomaly_impact_usd": impact,
                        "percentage_impact": percentage,
                        "usage_types": usage_types,
                        "hourly_price_usd": hourly_price
                    },
                    "recommendation": "Validate whether the GPU instance is required. Stop idle workloads, schedule non-production usage, or move to a smaller/cheaper instance where possible.",
                    "estimated_monthly_savings_usd": monthly_projection,
                    "risk": "medium",
                    "effort": "medium",
                    "priority_score": 95,
                    "requires_approval": True,
                    "implementation_steps": [
                        "Confirm owner and workload purpose.",
                        "Check whether this was temporary AI, embedding, or indexing workload.",
                        "Review utilization metrics and running hours.",
                        "Stop or schedule the instance if non-production.",
                        "Evaluate smaller instance type or Savings Plan only if usage is steady."
                    ]
                })

            elif "OpenSearch" in service:
                plans.append({
                    "category": "OpenSearch",
                    "action": "Optimize OpenSearch OCU usage",
                    "service": service,
                    "evidence": {
                        "anomaly_impact_usd": impact,
                        "percentage_impact": percentage,
                        "usage_types": usage_types
                    },
                    "recommendation": "Review SearchOCU and IndexingOCU usage. Reduce indexing load, pause unused collections/domains, tune retention, and validate whether this workload was temporary.",
                    "estimated_monthly_savings_usd": round(impact * 30, 2),
                    "risk": "medium",
                    "effort": "medium",
                    "priority_score": 92,
                    "requires_approval": True,
                    "implementation_steps": [
                        "Identify OpenSearch collection or domain responsible for the spike.",
                        "Check indexing jobs, vector ingestion, and search traffic.",
                        "Reduce retention or delete unused indexes.",
                        "Stop unused development/test search resources.",
                        "Add budget alert for OpenSearch."
                    ]
                })

            elif "Elastic Block Store" in service:
                plans.append({
                    "category": "EBS",
                    "action": "Review provisioned IOPS and unused volumes",
                    "service": service,
                    "evidence": {
                        "anomaly_impact_usd": impact,
                        "percentage_impact": percentage,
                        "usage_types": usage_types
                    },
                    "recommendation": "Review io1/io2 or provisioned IOPS volumes. Remove unused volumes, reduce provisioned IOPS, or migrate to gp3 where suitable.",
                    "estimated_monthly_savings_usd": round(impact * 30, 2),
                    "risk": "medium",
                    "effort": "medium",
                    "priority_score": 88,
                    "requires_approval": True,
                    "implementation_steps": [
                        "List unattached EBS volumes.",
                        "Identify provisioned IOPS volumes.",
                        "Snapshot critical volumes before changes.",
                        "Reduce IOPS or migrate to gp3 if workload allows.",
                        "Delete unused volumes after approval."
                    ]
                })

            elif "WAF" in service:
                plans.append({
                    "category": "Security Cost",
                    "action": "Review AWS WAF rule usage",
                    "service": service,
                    "evidence": {
                        "anomaly_impact_usd": impact,
                        "percentage_impact": percentage
                    },
                    "recommendation": "Review WAF WebACLs, managed rules, request volume, and unused rule groups.",
                    "estimated_monthly_savings_usd": round(impact * 30, 2),
                    "risk": "low",
                    "effort": "low",
                    "priority_score": 65,
                    "requires_approval": True,
                    "implementation_steps": [
                        "Identify active WebACLs and associated resources.",
                        "Check request volume spike.",
                        "Remove unused rule groups.",
                        "Keep security-critical rules enabled."
                    ]
                })

            else:
                plans.append({
                    "category": "Cost Anomaly",
                    "action": f"Investigate {service} anomaly",
                    "service": service,
                    "evidence": {
                        "anomaly_impact_usd": impact,
                        "percentage_impact": percentage,
                        "usage_types": usage_types
                    },
                    "recommendation": f"Investigate abnormal spend increase for {service}.",
                    "estimated_monthly_savings_usd": round(impact * 30, 2),
                    "risk": "medium",
                    "effort": "medium",
                    "priority_score": 70,
                    "requires_approval": False,
                    "implementation_steps": [
                        "Identify account, region, and usage type.",
                        "Check recent deployment or workload activity.",
                        "Confirm whether spend was expected.",
                        "Stop or reduce unnecessary resources."
                    ]
                })

        return plans

    def _plan_from_budgets(self, budgets: Dict[str, Any]):
        budget_data = budgets.get("budgets", {}).get("data", {})
        budgets_found = budget_data.get("budgets_found", 0)

        if budgets_found == 0:
            return [{
                "category": "Governance",
                "action": "Create AWS Budgets",
                "service": "AWS Budgets",
                "evidence": {
                    "budgets_found": budgets_found
                },
                "recommendation": "Create monthly AWS Budgets for total account spend and separate alerts for EC2, OpenSearch, SageMaker, and Bedrock.",
                "estimated_monthly_savings_usd": 0,
                "risk": "low",
                "effort": "low",
                "priority_score": 84,
                "requires_approval": False,
                "implementation_steps": [
                    "Create total monthly cost budget.",
                    "Create service-level budget alerts for EC2 and OpenSearch.",
                    "Set 50%, 80%, and 100% thresholds.",
                    "Send alerts to email or SNS."
                ]
            }]

        return []

    def _plan_from_compute_optimizer(self, compute_optimization: Dict[str, Any]):
        recommendations = compute_optimization.get("recommendations", [])

        if not recommendations:
            return [{
                "category": "Compute Optimizer",
                "action": "Enable or validate Compute Optimizer coverage",
                "service": "EC2",
                "evidence": {
                    "recommendations_found": 0
                },
                "recommendation": "No Compute Optimizer recommendations were found. Validate whether Compute Optimizer is enabled and has enough utilization history.",
                "estimated_monthly_savings_usd": 0,
                "risk": "low",
                "effort": "low",
                "priority_score": 60,
                "requires_approval": False,
                "implementation_steps": [
                    "Confirm Compute Optimizer is enabled.",
                    "Wait for enough CloudWatch history.",
                    "Re-run analysis after 24-48 hours.",
                    "Use CloudWatch metrics as fallback."
                ]
            }]

        plans = []

        for rec in recommendations:
            plans.append({
                "category": "Compute Optimizer",
                "action": "Apply Compute Optimizer recommendation",
                "service": "EC2",
                "evidence": rec,
                "recommendation": rec.get("recommendation", "Apply rightsizing recommendation."),
                "estimated_monthly_savings_usd": float(rec.get("estimated_savings_usd", 0) or 0),
                "risk": "medium",
                "effort": "medium",
                "priority_score": 86,
                "requires_approval": True,
                "implementation_steps": [
                    "Validate recommendation with workload owner.",
                    "Check utilization during peak period.",
                    "Schedule maintenance window.",
                    "Apply resize or family change.",
                    "Monitor after change."
                ]
            })

        return plans

    def _plan_from_ec2_discovery(self, ec2_discovery: Dict[str, Any], cloudwatch: Dict[str, Any]):
        discovery = ec2_discovery.get("ec2_discovery", {}).get("data", {})
        instances = discovery.get("instances", [])

        plans = []

        for instance in instances:
            instance_id = instance.get("instance_id")
            state = instance.get("state")

            if state == "stopped":
                plans.append({
                    "category": "EC2",
                    "action": "Terminate or archive stopped instance",
                    "service": "EC2",
                    "resource_id": instance_id,
                    "evidence": instance,
                    "recommendation": "Review stopped EC2 instance and terminate it if it is no longer required.",
                    "estimated_monthly_savings_usd": 0,
                    "risk": "low",
                    "effort": "low",
                    "priority_score": 82,
                    "requires_approval": True,
                    "implementation_steps": [
                        "Confirm owner.",
                        "Create AMI if rollback is required.",
                        "Check attached EBS volumes.",
                        "Terminate instance after approval."
                    ]
                })

        return plans

    def _plan_from_top_services(self, cost_analysis: Dict[str, Any]):
        summary = cost_analysis.get("cost_summary", {})
        top_services = summary.get("top_services", [])

        plans = []

        for item in top_services[:3]:
            service = item.get("service")
            amount = float(item.get("amount") or 0)

            if service and amount > 5:
                plans.append({
                    "category": "Top Spend Review",
                    "action": f"Review {service} spend",
                    "service": service,
                    "evidence": {
                        "seven_day_cost_usd": amount
                    },
                    "recommendation": f"{service} is a top cost contributor. Review usage, ownership, and optimization options.",
                    "estimated_monthly_savings_usd": round(amount * 0.2 * 4.3, 2),
                    "risk": "low",
                    "effort": "low",
                    "priority_score": 72,
                    "requires_approval": False,
                    "implementation_steps": [
                        "Identify resource owner.",
                        "Check usage trend.",
                        "Review tags and environment.",
                        "Apply service-specific optimization."
                    ]
                })

        return plans

    def _rank(self, opportunities: List[Dict[str, Any]]):
        deduped = {}

        for item in opportunities:
            key = f"{item.get('category')}::{item.get('action')}::{item.get('service')}::{item.get('resource_id', '')}"
            if key not in deduped:
                deduped[key] = item

        return sorted(
            deduped.values(),
            key=lambda item: (
                item.get("priority_score", 0),
                item.get("estimated_monthly_savings_usd", 0)
            ),
            reverse=True
        )

    def _extract_instance_type(self, usage_types: List[str]):
        for usage_type in usage_types:
            if usage_type and usage_type.startswith("BoxUsage:"):
                return usage_type.split("BoxUsage:")[-1]
        return None
