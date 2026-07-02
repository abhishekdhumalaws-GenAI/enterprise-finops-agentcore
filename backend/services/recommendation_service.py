class RecommendationService:
    def get_recommendations(self, service, total_cost):
        if total_cost == 0:
            return [
                f"No active {service or 'AWS'} cost detected for this period.",
                "Keep monitoring usage trends to detect future cost spikes."
            ]

        service_key = (service or "aws").lower()

        recommendations = {
            "opensearch": [
                "Review OpenSearch domain instance type and node count.",
                "Check if the domain is idle or underutilized.",
                "Review EBS volume size and storage type.",
                "Check replica count and availability zone configuration."
            ],
            "bedrock": [
                "Track model invocation volume and token usage.",
                "Use smaller models for simple tasks where possible.",
                "Cache repeated responses to reduce model calls.",
                "Optimize prompts to reduce input and output tokens."
            ],
            "lambda": [
                "Review function memory allocation and execution duration.",
                "Check high-invocation functions.",
                "Optimize cold starts and dependencies.",
                "Remove unused Lambda functions."
            ],
            "ec2": [
                "Identify idle or underutilized EC2 instances.",
                "Use Compute Optimizer for right-sizing recommendations.",
                "Stop non-production instances during off-hours.",
                "Consider Savings Plans or Reserved Instances."
            ],
            "s3": [
                "Enable lifecycle policies for old objects.",
                "Move infrequently accessed data to cheaper storage classes.",
                "Review incomplete multipart uploads.",
                "Check large buckets and unnecessary versions."
            ],
            "rds": [
                "Review idle or oversized database instances.",
                "Check storage growth and backup retention.",
                "Use Reserved Instances for steady workloads.",
                "Review Multi-AZ configuration where not required."
            ],
            "aws": [
                "Review top services by spend.",
                "Check cost anomalies and daily trends.",
                "Apply tagging for better cost allocation.",
                "Use budgets and alerts for proactive monitoring."
            ]
        }

        return recommendations.get(service_key, recommendations["aws"])
