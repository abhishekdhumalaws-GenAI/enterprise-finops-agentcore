def get_demo_execution_results():
    return {
        "organizations": {
            "agent": "Organizations Agent",
            "service": "AWS Organizations",
            "organizations": {
                "success": True,
                "data": {
                    "accounts_found": 3,
                    "accounts": [
                        {"account_id": "111111111111", "name": "prod"},
                        {"account_id": "222222222222", "name": "dev"},
                        {"account_id": "333333333333", "name": "sandbox"}
                    ]
                },
                "error": None
            }
        },
        "cost_analysis": {
            "agent": "Cost Analysis Agent",
            "service": "All AWS Services",
            "days": 7,
            "cost_summary": {
                "total_cost": 1290.75,
                "currency": "USD",
                "top_services": [
                    {"service": "Amazon Elastic Compute Cloud - Compute", "amount": 640.50},
                    {"service": "Amazon OpenSearch Service", "amount": 310.25},
                    {"service": "Amazon Elastic Block Store", "amount": 145.20},
                    {"service": "Amazon SageMaker", "amount": 110.30},
                    {"service": "AWS WAF", "amount": 84.50}
                ],
                "daily_totals": [
                    {"date": "2026-06-26", "amount": 95.0},
                    {"date": "2026-06-27", "amount": 110.5},
                    {"date": "2026-06-28", "amount": 135.25},
                    {"date": "2026-06-29", "amount": 620.0},
                    {"date": "2026-06-30", "amount": 125.0},
                    {"date": "2026-07-01", "amount": 105.0},
                    {"date": "2026-07-02", "amount": 100.0}
                ],
                "recommendation": "Highest spend is from EC2 GPU and OpenSearch OCU usage."
            },
            "recommendations": [
                "Review GPU EC2 usage.",
                "Optimize OpenSearch OCU usage.",
                "Review EBS provisioned IOPS.",
                "Create service-level budgets."
            ],
            "cost_data": []
        },
        "cur": {
            "agent": "Cost and Usage Report Agent",
            "service": "AWS CUR",
            "cur": {
                "success": True,
                "data": {
                    "cur_reports_found": 1,
                    "reports": [
                        {"report_name": "enterprise-finops-cur"}
                    ]
                },
                "error": None
            }
        },
        "cost_anomaly_detection": {
            "agent": "Anomaly Detection Agent",
            "success": True,
            "anomalies": [
                {
                    "dimension_value": "Amazon Elastic Compute Cloud - Compute",
                    "root_causes": [
                        {
                            "Service": "Amazon Elastic Compute Cloud - Compute",
                            "Region": "us-east-1",
                            "LinkedAccount": "111111111111",
                            "UsageType": "BoxUsage:g5.xlarge",
                            "Impact": {"Contribution": 410.0}
                        }
                    ],
                    "total_impact": 410.0,
                    "total_actual_spend": 640.5,
                    "total_expected_spend": 230.5,
                    "percentage_impact": 177.87
                },
                {
                    "dimension_value": "Amazon OpenSearch Service",
                    "root_causes": [
                        {
                            "Service": "Amazon OpenSearch Service",
                            "Region": "us-east-1",
                            "UsageType": "USE1-SearchOCU",
                            "Impact": {"Contribution": 120.0}
                        },
                        {
                            "Service": "Amazon OpenSearch Service",
                            "Region": "us-east-1",
                            "UsageType": "USE1-IndexingOCU",
                            "Impact": {"Contribution": 145.0}
                        }
                    ],
                    "total_impact": 265.0,
                    "total_actual_spend": 310.25,
                    "total_expected_spend": 45.25,
                    "percentage_impact": 585.64
                },
                {
                    "dimension_value": "Amazon Elastic Block Store",
                    "root_causes": [
                        {
                            "Service": "Amazon Elastic Block Store",
                            "Region": "us-east-1",
                            "UsageType": "EBS:VolumeP-IOPS.piops",
                            "Impact": {"Contribution": 95.0}
                        }
                    ],
                    "total_impact": 95.0,
                    "total_actual_spend": 145.2,
                    "total_expected_spend": 50.2,
                    "percentage_impact": 189.24
                },
                {
                    "dimension_value": "AWS WAF",
                    "root_causes": [
                        {
                            "Service": "AWS WAF",
                            "Impact": {"Contribution": 35.0}
                        }
                    ],
                    "total_impact": 35.0,
                    "total_actual_spend": 84.5,
                    "total_expected_spend": 49.5,
                    "percentage_impact": 70.7
                }
            ]
        },
        "pricing": {
            "agent": "Pricing Agent",
            "service": "EC2",
            "pricing": {
                "success": True,
                "data": {
                    "service": "EC2",
                    "region": "US East (N. Virginia)",
                    "instance_type": "g5.xlarge",
                    "operating_system": "Linux",
                    "tenancy": "Shared",
                    "price_found": True,
                    "price_per_hour_usd": 1.006,
                    "unit": "Hrs",
                    "description": "$1.006 per On Demand Linux g5.xlarge Instance Hour"
                },
                "error": None
            }
        },
        "budgets": {
            "agent": "Budgets Agent",
            "service": "AWS Budgets",
            "budgets": {
                "success": True,
                "data": {
                    "account_id": "111111111111",
                    "budgets_found": 0,
                    "budgets": []
                },
                "error": None
            }
        },
        "ec2_discovery": {
            "agent": "EC2 Discovery Agent",
            "service": "Amazon EC2",
            "discovery_type": "instances",
            "instance_type": "g5.xlarge",
            "ec2_discovery": {
                "success": True,
                "data": {
                    "instance_type_filter": "g5.xlarge",
                    "instances_found": 1,
                    "instances": [
                        {
                            "instance_id": "i-demo123456789",
                            "instance_type": "g5.xlarge",
                            "state": "running",
                            "environment": "dev"
                        }
                    ]
                },
                "error": None
            }
        },
        "cloudwatch": {
            "agent": "CloudWatch Agent",
            "service": "Amazon CloudWatch",
            "metric": "CPUUtilization",
            "cloudwatch": {
                "success": True,
                "data": {
                    "metric_found": True,
                    "instance_id": "i-demo123456789",
                    "cpu_average": 6.4,
                    "cpu_maximum": 18.2
                },
                "error": None
            }
        },
        "compute_optimization": {
            "agent": "Compute Optimization Agent",
            "service": "EC2",
            "optimization_type": "rightsizing",
            "recommendations": [
                {
                    "resource_id": "i-demo123456789",
                    "recommendation": "Downsize g5.xlarge to g4dn.xlarge or schedule non-production runtime.",
                    "estimated_savings_usd": 320.0,
                    "risk": "medium"
                }
            ]
        }
    }
