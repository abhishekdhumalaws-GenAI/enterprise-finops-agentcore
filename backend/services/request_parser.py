class RequestParser:
    def parse(self, user_query: str):
        query = user_query.lower()

        service = None
        intent = "cost_analysis"

        if (
            "anomaly" in query
            or "anomalies" in query
            or "spike" in query
            or "unusual charge" in query
            or "unusual cost" in query
            or "bill increase" in query
        ):
            intent = "cost_anomaly_detection"
            service = "Cost Anomaly Detection"

        elif "trusted advisor" in query or "unused resource" in query or "unused aws" in query:
            intent = "governance_optimization"
            service = "Trusted Advisor"

        elif (
            "rightsizing" in query
            or "right sizing" in query
            or "optimize ec2" in query
            or "ec2 optimization" in query
            or "idle ec2" in query
            or "underutilized" in query
        ):
            intent = "compute_optimization"
            service = "EC2"

        elif "opensearch" in query or "open search" in query:
            service = "OpenSearch"
        elif "bedrock" in query:
            service = "Bedrock"
        elif "lambda" in query:
            service = "Lambda"
        elif "ec2" in query or "instance" in query:
            service = "EC2"
        elif "s3" in query or "storage" in query:
            service = "S3"
        elif "rds" in query or "database" in query:
            service = "RDS"

        days = 7
        if "30" in query or "month" in query:
            days = 30
        elif "90" in query or "quarter" in query:
            days = 90
        elif "yesterday" in query:
            days = 1

        return {
            "intent": intent,
            "service": service,
            "days": days,
            "metric": "UnblendedCost"
        }
