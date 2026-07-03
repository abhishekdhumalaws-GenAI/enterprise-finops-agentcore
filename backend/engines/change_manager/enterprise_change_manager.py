from datetime import datetime, timezone
from typing import Dict, Any


class EnterpriseChangeManager:
    def __init__(self):
        self.name = "Enterprise Change Manager"

    def create_change_requests(self, approval_result: Dict[str, Any]) -> Dict[str, Any]:
        approvals = approval_result.get("approval_requests", [])
        changes = []

        for approval in approvals:
            financial = approval.get("financial_impact", {})
            risk = approval.get("risk_assessment", {})
            execution = approval.get("execution_plan", {})

            changes.append({
                "change_id": approval.get("approval_id", "").replace("approval-", "change-"),
                "status": "PENDING_CHANGE_APPROVAL",
                "title": self._title(approval),
                "service": approval.get("service"),
                "category": approval.get("category"),
                "business_justification": (
                    f"Potential monthly savings: ${financial.get('monthly_savings_usd', 0)}. "
                    f"Potential annual savings: ${financial.get('annual_savings_usd', 0)}. "
                    f"Business impact: {financial.get('business_impact')}."
                ),
                "risk_level": risk.get("risk"),
                "risk_score": risk.get("risk_score"),
                "technical_risk": risk.get("technical_risk"),
                "business_risk": risk.get("business_risk"),
                "approver": approval.get("approver"),
                "approval_status": "PENDING_APPROVAL",
                "maintenance_window": self._maintenance_window(approval),
                "execution_mode": "MANUAL_APPROVAL_REQUIRED",
                "execution_steps": execution.get("steps", []),
                "pre_checks": execution.get("pre_checks", []),
                "post_checks": execution.get("post_checks", []),
                "rollback_plan": approval.get("rollback_plan", []),
                "validation_plan": self._validation_plan(approval),
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        return {
            "engine": self.name,
            "status": "success",
            "change_requests_count": len(changes),
            "change_requests": changes
        }

    def _title(self, approval: Dict[str, Any]) -> str:
        return f"{approval.get('category')} change: {approval.get('action')}"

    def _maintenance_window(self, approval: Dict[str, Any]) -> Dict[str, Any]:
        category = approval.get("category")

        if category in ["EC2", "OpenSearch", "EBS"]:
            return {
                "required": True,
                "recommended_window": "Sunday 02:00-04:00 UTC",
                "reason": "Infrastructure change may impact availability or performance."
            }

        return {
            "required": False,
            "recommended_window": "Business hours",
            "reason": "Low-risk review or configuration change."
        }

    def _validation_plan(self, approval: Dict[str, Any]):
        category = approval.get("category")

        common = [
            "Verify cost trend after change.",
            "Confirm no unexpected service errors.",
            "Record realized savings."
        ]

        if category == "EC2":
            return [
                "Check instance state.",
                "Validate application health.",
                "Review CPU, memory, network, and disk metrics.",
                "Confirm no user-facing errors."
            ] + common

        if category == "OpenSearch":
            return [
                "Check cluster or collection health.",
                "Validate indexing success.",
                "Review search latency.",
                "Confirm no ingestion failures."
            ] + common

        if category == "EBS":
            return [
                "Validate volume state.",
                "Check disk latency and IOPS.",
                "Confirm application can read/write normally.",
                "Verify snapshots are available."
            ] + common

        if category == "Security Cost":
            return [
                "Confirm WAF WebACL remains attached.",
                "Verify no critical rule was removed.",
                "Review blocked/allowed request metrics.",
                "Confirm application remains protected."
            ] + common

        return common
