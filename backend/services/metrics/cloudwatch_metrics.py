import os
from typing import Dict, Any

import boto3


class CloudWatchMetrics:
    def __init__(self):
        self.namespace = os.getenv("CLOUDWATCH_NAMESPACE", "EnterpriseFinOps")
        self.client = boto3.client("cloudwatch")

    def put_metric(self, name: str, value: float, unit: str = "Count"):
        self.client.put_metric_data(
            Namespace=self.namespace,
            MetricData=[
                {
                    "MetricName": name,
                    "Value": value,
                    "Unit": unit
                }
            ]
        )

    def publish_analysis_metrics(self, result: Dict[str, Any]):
        decision = result.get("decision_engine", {})
        approval = result.get("approval_workflow", {})
        optimization = result.get("optimization_plan", {})

        summary = decision.get("summary", {})
        opt_summary = optimization.get("optimization_summary", {})

        self.put_metric(
            "EstimatedMonthlySavings",
            float(summary.get("estimated_monthly_savings_usd", 0)),
            "None"
        )

        self.put_metric(
            "EstimatedAnnualSavings",
            float(summary.get("estimated_annual_savings_usd", 0)),
            "None"
        )

        self.put_metric(
            "OptimizationOpportunities",
            float(opt_summary.get("total_opportunities", 0)),
            "Count"
        )

        self.put_metric(
            "PendingApprovals",
            float(approval.get("approval_count", 0)),
            "Count"
        )

    def publish_execution_metrics(self, result: Dict[str, Any]):
        status = result.get("status")

        self.put_metric("ExecutionRequests", 1, "Count")

        if status == "success":
            self.put_metric("ExecutionSuccess", 1, "Count")
        else:
            self.put_metric("ExecutionFailure", 1, "Count")
