from datetime import datetime, timezone
from typing import Dict, Any, List


class AIReasoningEngine:
    """
    Converts decision-engine output into enterprise-grade reasoning:
    evidence, hypothesis, risks, approvals, execution plan, rollback plan.
    """

    def generate(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        decisions = decision_result.get("decisions", [])

        reasoning_items = []

        for decision in decisions:
            reasoning_items.append({
                "service": decision.get("service"),
                "category": decision.get("category"),
                "action": decision.get("action"),
                "hypothesis": self._build_hypothesis(decision),
                "evidence_summary": self._build_evidence(decision),
                "financial_impact": {
                    "monthly_savings_usd": decision.get("estimated_monthly_savings_usd", 0),
                    "annual_savings_usd": decision.get("estimated_annual_savings_usd", 0),
                    "business_impact": decision.get("business_impact")
                },
                "risk_assessment": {
                    "risk": decision.get("risk"),
                    "risk_score": decision.get("risk_score"),
                    "technical_risk": self._technical_risk(decision),
                    "business_risk": self._business_risk(decision)
                },
                "confidence": {
                    "score": decision.get("confidence_score"),
                    "reason": self._confidence_reason(decision)
                },
                "approval_path": self._approval_path(decision),
                "execution_plan": self._execution_plan(decision),
                "rollback_plan": self._rollback_plan(decision),
                "final_decision": decision.get("decision")
            })

        return {
            "engine": "ai_reasoning_engine",
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "items_reasoned": len(reasoning_items),
                "approval_required": len([
                    item for item in reasoning_items
                    if item["approval_path"]["approval_required"]
                ])
            },
            "reasoning": reasoning_items
        }

    def _build_hypothesis(self, decision: Dict[str, Any]) -> str:
        service = decision.get("service", "Unknown service")
        category = decision.get("category", "")

        if category == "EC2":
            return (
                "The cost increase is likely caused by GPU-based EC2 usage, "
                "possibly from AI inference, embedding generation, model experimentation, "
                "or batch processing workloads."
            )

        if category == "OpenSearch":
            return (
                "The cost increase is likely caused by indexing or search capacity usage, "
                "possibly from vector indexing, search traffic, or bulk ingestion."
            )

        if category == "EBS":
            return (
                "The cost increase is likely caused by provisioned IOPS or high-performance "
                "EBS volume usage that may not be required continuously."
            )

        if category == "Governance":
            return (
                "The account lacks proactive cost guardrails, increasing the chance of "
                "undetected spend spikes."
            )

        return f"The spend pattern for {service} requires investigation to confirm whether usage was expected."

    def _build_evidence(self, decision: Dict[str, Any]) -> List[str]:
        evidence = decision.get("evidence", {})
        output = []

        if "anomaly_impact_usd" in evidence:
            output.append(f"Anomaly impact detected: ${evidence.get('anomaly_impact_usd')}")

        if "percentage_impact" in evidence and evidence.get("percentage_impact") is not None:
            output.append(f"Percentage impact: {evidence.get('percentage_impact')}%")

        if "usage_types" in evidence and evidence.get("usage_types"):
            output.append(f"Usage types: {', '.join(evidence.get('usage_types'))}")

        if "hourly_price_usd" in evidence and evidence.get("hourly_price_usd"):
            output.append(f"Hourly price: ${evidence.get('hourly_price_usd')}")

        if "budgets_found" in evidence:
            output.append(f"Budgets found: {evidence.get('budgets_found')}")

        if "recommendations_found" in evidence:
            output.append(f"Compute Optimizer recommendations found: {evidence.get('recommendations_found')}")

        if "seven_day_cost_usd" in evidence:
            output.append(f"Seven-day cost: ${evidence.get('seven_day_cost_usd')}")

        if not output:
            output.append("Evidence is limited; additional usage and ownership data is required.")

        return output

    def _technical_risk(self, decision: Dict[str, Any]) -> str:
        category = decision.get("category")

        if category == "EC2":
            return "Stopping or resizing compute may impact workload availability or performance."
        if category == "OpenSearch":
            return "Changing capacity, retention, or indexes may impact search latency or ingestion throughput."
        if category == "EBS":
            return "Reducing IOPS or deleting volumes may impact storage performance or data availability."
        if category == "Security Cost":
            return "Removing WAF rules may reduce security coverage if not reviewed carefully."
        return "Low technical risk if reviewed before execution."

    def _business_risk(self, decision: Dict[str, Any]) -> str:
        savings = decision.get("estimated_monthly_savings_usd", 0)

        if savings >= 500:
            return "High-value optimization; incorrect action could affect important workloads."
        if decision.get("requires_approval"):
            return "Business owner approval required before implementation."
        return "Low business risk."

    def _confidence_reason(self, decision: Dict[str, Any]) -> str:
        score = decision.get("confidence_score", 0)

        if score >= 90:
            return "High confidence because recommendation is backed by anomaly, pricing, priority, and implementation evidence."
        if score >= 70:
            return "Medium confidence; recommendation is valid but could benefit from additional utilization data."
        return "Low confidence; more evidence is required before action."

    def _approval_path(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        required = decision.get("requires_approval", False)

        if not required:
            return {
                "approval_required": False,
                "approver": None,
                "reason": "No infrastructure change is directly executed."
            }

        category = decision.get("category")

        approver = "Cloud Platform Owner"

        if category == "EC2":
            approver = "Application Owner + Cloud Platform Owner"
        elif category == "OpenSearch":
            approver = "Search Platform Owner + Application Owner"
        elif category == "EBS":
            approver = "Storage Owner + Application Owner"
        elif category == "Security Cost":
            approver = "Security Owner"

        return {
            "approval_required": True,
            "approver": approver,
            "reason": "Recommendation may change infrastructure, performance, availability, or security posture."
        }

    def _execution_plan(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "mode": "manual_approval_first",
            "steps": decision.get("engineering_plan", []),
            "pre_checks": [
                "Confirm resource owner.",
                "Validate environment: production or non-production.",
                "Check recent usage and business criticality.",
                "Confirm rollback option."
            ],
            "post_checks": [
                "Monitor cost for 24-48 hours.",
                "Monitor service health metrics.",
                "Validate application behavior.",
                "Record realized savings."
            ]
        }

    def _rollback_plan(self, decision: Dict[str, Any]) -> List[str]:
        category = decision.get("category")

        if category == "EC2":
            return [
                "Record current instance type and configuration.",
                "Create AMI or snapshot if required.",
                "If performance degrades, revert to previous instance type.",
                "Restore original schedule or capacity settings."
            ]

        if category == "OpenSearch":
            return [
                "Export index settings before modification.",
                "Record current capacity and retention configuration.",
                "If latency or ingestion errors increase, restore previous capacity.",
                "Re-enable paused collections/domains if required."
            ]

        if category == "EBS":
            return [
                "Snapshot volume before changing IOPS or deleting volume.",
                "Record original volume type and IOPS.",
                "Restore from snapshot if data or performance issue occurs.",
                "Reapply previous IOPS configuration if needed."
            ]

        return [
            "Document current configuration.",
            "Apply change in controlled manner.",
            "Monitor results.",
            "Revert to previous configuration if issues occur."
        ]
