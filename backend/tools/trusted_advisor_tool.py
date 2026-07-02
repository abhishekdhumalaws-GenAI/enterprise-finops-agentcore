import boto3
from botocore.exceptions import ClientError, BotoCoreError

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class TrustedAdvisorTool:
    def __init__(self):
        self.client = boto3.client("support", region_name="us-east-1")

    def get_cost_optimization_checks(self):
        try:
            checks_response = self.client.describe_trusted_advisor_checks(
                language="en"
            )

            cost_checks = [
                check for check in checks_response.get("checks", [])
                if check.get("category") == "cost_optimizing"
            ]

            results = []

            for check in cost_checks:
                check_id = check["id"]

                result = self.client.describe_trusted_advisor_check_result(
                    checkId=check_id,
                    language="en"
                )

                check_result = result.get("result", {})

                results.append({
                    "check_id": check_id,
                    "name": check.get("name"),
                    "category": check.get("category"),
                    "status": check_result.get("status"),
                    "resources_summary": check_result.get("resourcesSummary", {}),
                    "flagged_resources": check_result.get("flaggedResources", [])[:10]
                })

            return results

        except ClientError as error:
            logger.error(f"Trusted Advisor ClientError: {error}")
            return {
                "error": True,
                "type": "AWS_CLIENT_ERROR",
                "message": str(error)
            }

        except BotoCoreError as error:
            logger.error(f"Trusted Advisor BotoCoreError: {error}")
            return {
                "error": True,
                "type": "AWS_BOTOCORE_ERROR",
                "message": str(error)
            }
