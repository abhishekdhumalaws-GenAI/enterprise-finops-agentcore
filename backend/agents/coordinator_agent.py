class FinOpsCoordinatorAgent:
    def __init__(self):
        self.name = "FinOps Coordinator Agent"

    def analyze_request(self, user_query: str):
        query = user_query.lower()

        # EC2
        if "ec2" in query or "instance" in query:
            return {
                "agent": "ec2_cost_agent",
                "task": "Analyze EC2 cost and rightsizing opportunities"
            }

        # S3
        if "s3" in query or "storage" in query:
            return {
                "agent": "s3_cost_agent",
                "task": "Analyze S3 storage cost and lifecycle optimization"
            }

        # RDS
        if "rds" in query or "database" in query:
            return {
                "agent": "rds_cost_agent",
                "task": "Analyze RDS cost and optimization opportunities"
            }

        # OpenSearch
        if "opensearch" in query or "open search" in query:
            return {
                "agent": "opensearch_cost_agent",
                "task": "Analyze Amazon OpenSearch Service cost and optimization opportunities"
            }

        # Bedrock
        if "bedrock" in query or "foundation model" in query or "llm" in query:
            return {
                "agent": "bedrock_cost_agent",
                "task": "Analyze Amazon Bedrock model usage and optimization opportunities"
            }

        # Lambda
        if "lambda" in query or "serverless" in query:
            return {
                "agent": "lambda_cost_agent",
                "task": "Analyze AWS Lambda execution cost and optimization opportunities"
            }

        # Overall AWS
        if "total" in query or "overall" in query or "aws cost" in query:
            return {
                "agent": "general_cost_agent",
                "task": "Analyze overall AWS cost optimization opportunities"
            }

        return {
            "agent": "general_cost_agent",
            "task": "Analyze overall AWS cost optimization opportunities"
        }
