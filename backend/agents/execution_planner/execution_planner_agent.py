from datetime import datetime, timezone
from typing import Dict, Any


class ExecutionPlannerAgent:
    def __init__(self):
        self.name = "Execution Planner Agent"

    def create_execution_plans(self, change_result: Dict[str, Any]) -> Dict[str, Any]:
        changes = change_result.get("change_requests", [])
        execution_plans = []

        for change in changes:
            execution_plans.append({
                "execution_id": change.get("change_id", "").replace("change-", "exec-"),
                "change_id": change.get("change_id"),
                "status": "READY_FOR_APPROVAL",
                "execution_mode": "DRY_RUN_ONLY",
                "service": change.get("service"),
                "category": change.get("category"),
                "title": change.get("title"),
                "approver": change.get("approver"),
                "approval_status": change.get("approval_status"),
                "maintenance_window": change.get("maintenance_window"),
                "pre_checks": change.get("pre_checks", []),
                "execution_steps": self._build_execution_steps(change),
                "validation_steps": change.get("validation_plan", []),
                "rollback_steps": change.get("rollback_plan", []),
                "safety_controls": [
                    "No AWS resource will be modified in dry-run mode.",
                    "Execution requires explicit approval.",
                    "Rollback plan must exist before live execution.",
                    "Post-change validation is mandatory."
                ],
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        return {
            "agent": self.name,
            "status": "success",
            "execution_plans_count": len(execution_plans),
            "execution_mode": "DRY_RUN_ONLY",
            "execution_plans": execution_plans
        }

    def _build_execution_steps(self, change: Dict[str, Any]):
        category = change.get("category")

        if category == "EC2":
            return [
                {
                    "step": 1,
                    "type": "precheck",
                    "description": "Describe EC2 instance and confirm current state.",
                    "aws_action": "ec2:DescribeInstances",
                    "dry_run": True
                },
                {
                    "step": 2,
                    "type": "backup",
                    "description": "Create AMI or snapshot if required.",
                    "aws_action": "ec2:CreateImage",
                    "dry_run": True
                },
                {
                    "step": 3,
                    "type": "change",
                    "description": "Stop, schedule, or resize EC2 instance after approval.",
                    "aws_action": "ec2:StopInstances / ec2:ModifyInstanceAttribute",
                    "dry_run": True
                },
                {
                    "step": 4,
                    "type": "validation",
                    "description": "Validate instance health and CloudWatch metrics.",
                    "aws_action": "cloudwatch:GetMetricData",
                    "dry_run": True
                }
            ]

        if category == "OpenSearch":
            return [
                {
                    "step": 1,
                    "type": "precheck",
                    "description": "Describe OpenSearch domain or serverless collection.",
                    "aws_action": "opensearch:DescribeDomain / aoss:ListCollections",
                    "dry_run": True
                },
                {
                    "step": 2,
                    "type": "analysis",
                    "description": "Identify indexing/search OCU drivers.",
                    "aws_action": "cloudwatch:GetMetricData",
                    "dry_run": True
                },
                {
                    "step": 3,
                    "type": "change",
                    "description": "Tune retention, indexing workload, or capacity after approval.",
                    "aws_action": "opensearch:UpdateDomainConfig / aoss:UpdateCollection",
                    "dry_run": True
                },
                {
                    "step": 4,
                    "type": "validation",
                    "description": "Validate search latency, indexing health, and errors.",
                    "aws_action": "cloudwatch:GetMetricData",
                    "dry_run": True
                }
            ]

        if category == "EBS":
            return [
                {
                    "step": 1,
                    "type": "precheck",
                    "description": "List EBS volumes and identify provisioned IOPS volumes.",
                    "aws_action": "ec2:DescribeVolumes",
                    "dry_run": True
                },
                {
                    "step": 2,
                    "type": "backup",
                    "description": "Snapshot target volume before modification.",
                    "aws_action": "ec2:CreateSnapshot",
                    "dry_run": True
                },
                {
                    "step": 3,
                    "type": "change",
                    "description": "Reduce IOPS, migrate to gp3, or remove unused volume after approval.",
                    "aws_action": "ec2:ModifyVolume / ec2:DeleteVolume",
                    "dry_run": True
                },
                {
                    "step": 4,
                    "type": "validation",
                    "description": "Validate volume health, latency, and application access.",
                    "aws_action": "cloudwatch:GetMetricData",
                    "dry_run": True
                }
            ]

        if category == "Security Cost":
            return [
                {
                    "step": 1,
                    "type": "precheck",
                    "description": "List WAF WebACLs and rule groups.",
                    "aws_action": "wafv2:ListWebACLs / wafv2:ListRuleGroups",
                    "dry_run": True
                },
                {
                    "step": 2,
                    "type": "analysis",
                    "description": "Review request volume and managed rule usage.",
                    "aws_action": "cloudwatch:GetMetricData",
                    "dry_run": True
                },
                {
                    "step": 3,
                    "type": "change",
                    "description": "Remove unused rule groups only after security approval.",
                    "aws_action": "wafv2:UpdateWebACL",
                    "dry_run": True
                },
                {
                    "step": 4,
                    "type": "validation",
                    "description": "Validate WAF remains attached and security coverage is preserved.",
                    "aws_action": "wafv2:GetWebACL",
                    "dry_run": True
                }
            ]

        return [
            {
                "step": 1,
                "type": "manual",
                "description": "Review change request manually.",
                "aws_action": None,
                "dry_run": True
            }
        ]
