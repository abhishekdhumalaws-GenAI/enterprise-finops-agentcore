from aws_cdk import (
    Stack,
    aws_cloudwatch as cloudwatch,
)
from constructs import Construct


class MonitoringStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        namespace = "EnterpriseFinOps"

        dashboard = cloudwatch.Dashboard(
            self,
            "EnterpriseFinOpsDashboard",
            dashboard_name="Enterprise-FinOps-Platform"
        )

        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Estimated Savings",
                left=[
                    cloudwatch.Metric(
                        namespace=namespace,
                        metric_name="EstimatedMonthlySavings",
                        statistic="Maximum"
                    ),
                    cloudwatch.Metric(
                        namespace=namespace,
                        metric_name="EstimatedAnnualSavings",
                        statistic="Maximum"
                    )
                ],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="Optimization Opportunities & Approvals",
                left=[
                    cloudwatch.Metric(
                        namespace=namespace,
                        metric_name="OptimizationOpportunities",
                        statistic="Maximum"
                    ),
                    cloudwatch.Metric(
                        namespace=namespace,
                        metric_name="PendingApprovals",
                        statistic="Maximum"
                    )
                ],
                width=12
            )
        )

        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Execution Activity",
                left=[
                    cloudwatch.Metric(
                        namespace=namespace,
                        metric_name="ExecutionRequests",
                        statistic="Sum"
                    ),
                    cloudwatch.Metric(
                        namespace=namespace,
                        metric_name="ExecutionSuccess",
                        statistic="Sum"
                    ),
                    cloudwatch.Metric(
                        namespace=namespace,
                        metric_name="ExecutionFailure",
                        statistic="Sum"
                    )
                ],
                width=12
            ),
            cloudwatch.SingleValueWidget(
                title="Current Pending Approvals",
                metrics=[
                    cloudwatch.Metric(
                        namespace=namespace,
                        metric_name="PendingApprovals",
                        statistic="Maximum"
                    )
                ],
                width=12
            )
        )
