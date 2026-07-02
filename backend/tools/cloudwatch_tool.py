from datetime import datetime, timedelta, timezone

from botocore.exceptions import ClientError, BotoCoreError

from backend.config.settings import settings
from backend.core.base_tool import BaseTool
from backend.services.aws_session_manager import AWSSessionManager
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class CloudWatchTool(BaseTool):
    name = "cloudwatch"

    def __init__(self):
        session = AWSSessionManager.get_session()
        self.client = session.client(
            "cloudwatch",
            region_name=settings.AWS_REGION
        )

    def execute(
        self,
        namespace: str = "AWS/EC2",
        metric_name: str = "CPUUtilization",
        dimension_name: str = "InstanceId",
        dimension_value: str | None = None,
        days: int = 7
    ):
        try:
            if not dimension_value:
                return self.success_response({
                    "metric_found": False,
                    "message": "No resource identifier provided for CloudWatch metric lookup."
                })

            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=days)

            response = self.client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=[
                    {
                        "Name": dimension_name,
                        "Value": dimension_value
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=["Average", "Maximum"],
                Unit="Percent"
            )

            datapoints = response.get("Datapoints", [])

            if not datapoints:
                return self.success_response({
                    "metric_found": False,
                    "namespace": namespace,
                    "metric_name": metric_name,
                    "dimension_name": dimension_name,
                    "dimension_value": dimension_value,
                    "message": "No CloudWatch datapoints found for this resource."
                })

            avg_values = [point["Average"] for point in datapoints if "Average" in point]
            max_values = [point["Maximum"] for point in datapoints if "Maximum" in point]

            avg_cpu = round(sum(avg_values) / len(avg_values), 2) if avg_values else None
            max_cpu = round(max(max_values), 2) if max_values else None

            return self.success_response({
                "metric_found": True,
                "namespace": namespace,
                "metric_name": metric_name,
                "dimension_name": dimension_name,
                "dimension_value": dimension_value,
                "days": days,
                "average": avg_cpu,
                "maximum": max_cpu,
                "datapoint_count": len(datapoints)
            })

        except ClientError as error:
            logger.error(f"CloudWatch ClientError: {error}")
            return self.error_response("AWS_CLIENT_ERROR", str(error))

        except BotoCoreError as error:
            logger.error(f"CloudWatch BotoCoreError: {error}")
            return self.error_response("AWS_BOTOCORE_ERROR", str(error))

        except Exception as error:
            logger.exception("Unexpected CloudWatch Tool error")
            return self.error_response("UNEXPECTED_ERROR", str(error))
