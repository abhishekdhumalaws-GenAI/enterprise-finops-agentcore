from botocore.exceptions import ClientError, BotoCoreError

from backend.services.aws_session_manager import AWSSessionManager
from backend.config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ComputeOptimizerTool:
    def __init__(self):
        session = AWSSessionManager.get_session()
        self.client = session.client(
            "compute-optimizer",
            region_name=settings.AWS_REGION
        )

    def get_ec2_recommendations(self):
        try:
            logger.info("Fetching EC2 rightsizing recommendations")

            response = self.client.get_ec2_instance_recommendations()

            recommendations = []

            for item in response.get("instanceRecommendations", []):
                recommendations.append({
                    "instance_arn": item.get("instanceArn"),
                    "account_id": item.get("accountId"),
                    "current_instance_type": item.get("currentInstanceType"),
                    "finding": item.get("finding"),
                    "recommendation_options": [
                        {
                            "instance_type": option.get("instanceType"),
                            "performance_risk": option.get("performanceRisk"),
                            "rank": option.get("rank")
                        }
                        for option in item.get("recommendationOptions", [])
                    ]
                })

            return recommendations

        except ClientError as error:
            logger.error(f"Compute Optimizer ClientError: {error}")
            return {
                "error": True,
                "type": "AWS_CLIENT_ERROR",
                "message": str(error)
            }

        except BotoCoreError as error:
            logger.error(f"Compute Optimizer BotoCoreError: {error}")
            return {
                "error": True,
                "type": "AWS_BOTOCORE_ERROR",
                "message": str(error)
            }

        except Exception as error:
            logger.exception("Unexpected Compute Optimizer error")
            return {
                "error": True,
                "type": "UNEXPECTED_ERROR",
                "message": str(error)
            }
