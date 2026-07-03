from datetime import datetime, timezone
from typing import Dict, Any, List


class AIDecisionEngine:
    """
    Enterprise FinOps AI Decision Engine.

    Converts optimization opportunities into decision-grade recommendations:
    - ROI score
    - risk score
    - confidence score
    - business impact
    - execution decision
    """

    def evaluate(self, optimization_plan: Dict[str, Any]) -> Dict[str, Any]:
        opportunities = optimization_plan.get("optimization_plan", [])

        decisions = []

        for item in opportunities:
            savings = float(item.get("estimated_monthly_savings_usd", 0) or 0)
            risk = item.get("risk", "medium")
            effort = item.get("effort", "medium")
            priority = int(item.get("priority_score", 0) or 0)

            roi_score = self._calculate_roi_score(savings, effort)
            risk_score = self._calculate_risk_score(risk)
            confidence_score = self._calculate_confidence_score(item)
            execution_decision = self._make_decision(
                priority_score=priority,
                roi_score=roi_score,
                risk_score=risk_score,
                confidence_score=confidence_score,
                requires_approval=item.get("requires_approval", False)
            )

            decisions.append({
                "category": item.get("category"),
                "service": item.get("service"),
                "action": item.get("action"),
                "recommendation": item.get("recommendation"),
                "estimated_monthly_savings_usd": savings,
                "estimated_annual_savings_usd": round(savings * 12, 2),
                "risk": risk,
                "risk_score": risk_score,
                "effort": effort,
                "roi_score": roi_score,
                "confidence_score": confidence_score,
                "priority_score": priority,
                "requires_approval": item.get("requires_approval", False),
                "decision": execution_decision,
                "business_impact": self._business_impact(savings, risk),
                "engineering_plan": item.get("implementation_steps", []),
                "evidence": item.get("evidence", {})
            })

        ranked_decisions = sorted(
            decisions,
            key=lambda x: (
                x["decision"]["execution_rank"],
                x["roi_score"],
                x["confidence_score"]
            ),
            reverse=True
        )

        return {
            "engine": "ai_decision_engine",
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_decisions": len(ranked_decisions),
                "auto_execute_candidates": len([
                    d for d in ranked_decisions
                    if d["decision"]["decision_type"] == "AUTO_EXECUTE_CANDIDATE"
                ]),
                "approval_required": len([
                    d for d in ranked_decisions
                    if d["requires_approval"]
                ]),
                "estimated_monthly_savings_usd": round(
                    sum(d["estimated_monthly_savings_usd"] for d in ranked_decisions),
                    2
                ),
                "estimated_annual_savings_usd": round(
                    sum(d["estimated_annual_savings_usd"] for d in ranked_decisions),
                    2
                ),
                "top_decision": ranked_decisions[0] if ranked_decisions else None
            },
            "decisions": ranked_decisions
        }

    def _calculate_roi_score(self, savings: float, effort: str) -> int:
        effort_multiplier = {
            "low": 1.0,
            "medium": 0.75,
            "high": 0.5
        }.get(effort, 0.75)

        if savings >= 500:
            base = 100
        elif savings >= 250:
            base = 85
        elif savings >= 100:
            base = 70
        elif savings >= 25:
            base = 55
        elif savings > 0:
            base = 35
        else:
            base = 10

        return round(base * effort_multiplier)

    def _calculate_risk_score(self, risk: str) -> int:
        return {
            "low": 20,
            "medium": 50,
            "high": 80
        }.get(risk, 50)

    def _calculate_confidence_score(self, item: Dict[str, Any]) -> int:
        evidence = item.get("evidence", {})
        score = 50

        if evidence:
            score += 20

        if item.get("estimated_monthly_savings_usd", 0) > 0:
            score += 10

        if item.get("priority_score", 0) >= 80:
            score += 10

        if item.get("implementation_steps"):
            score += 10

        return min(score, 100)

    def _make_decision(
        self,
        priority_score: int,
        roi_score: int,
        risk_score: int,
        confidence_score: int,
        requires_approval: bool
    ) -> Dict[str, Any]:

        if requires_approval:
            decision_type = "APPROVAL_REQUIRED"
            execution_rank = 70
            reason = "Optimization has savings potential but requires human approval."

        elif priority_score >= 80 and roi_score >= 60 and risk_score <= 50:
            decision_type = "AUTO_EXECUTE_CANDIDATE"
            execution_rank = 90
            reason = "High-priority, good ROI, and acceptable risk."

        elif confidence_score < 70:
            decision_type = "NEEDS_MORE_DATA"
            execution_rank = 40
            reason = "Recommendation requires more evidence before action."

        else:
            decision_type = "REVIEW_RECOMMENDED"
            execution_rank = 60
            reason = "Recommendation is valid but should be reviewed before execution."

        return {
            "decision_type": decision_type,
            "execution_rank": execution_rank,
            "reason": reason
        }

    def _business_impact(self, savings: float, risk: str) -> str:
        if savings >= 500:
            return "High financial impact"
        if savings >= 100:
            return "Medium financial impact"
        if savings > 0:
            return "Low financial impact"
        if risk == "low":
            return "Governance improvement"
        return "Operational improvement"
