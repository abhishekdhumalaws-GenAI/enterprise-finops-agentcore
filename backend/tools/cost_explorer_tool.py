import boto3
from botocore.exceptions import ClientError, BotoCoreError
from datetime import date, timedelta
from backend.services.aws_session_manager import AWSSessionManager

from backend.config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class CostExplorerTool:
    def __init__(self):
        session = AWSSessionManager.get_session()
        self.client = session.client(
            "ce",
            region_name=settings.AWS_REGION
	)

    def get_cost(self, days: int = 7, service_filter: str | None = None):
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            logger.info(
                f"Fetching cost data | days={days} | service_filter={service_filter}"
            )

            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.isoformat(),
                    "End": end_date.isoformat()
                },
                Granularity="DAILY",
                Metrics=[settings.COST_METRIC],
                GroupBy=[
                    {
                        "Type": "DIMENSION",
                        "Key": "SERVICE"
                    }
                ]
            )

            results = []

            for day in response["ResultsByTime"]:
                usage_date = day["TimePeriod"]["Start"]

                for group in day.get("Groups", []):
                    service_name = group["Keys"][0]
                    amount = float(group["Metrics"][settings.COST_METRIC]["Amount"])
                    unit = group["Metrics"][settings.COST_METRIC]["Unit"]

                    if service_filter:
                        if service_filter.lower() not in service_name.lower():
                            continue

                    if abs(amount) <= 0.0001:
                        continue

                    results.append({
                        "date": usage_date,
                        "service": service_name,
                        "amount": round(amount, 4),
                        "unit": unit
                    })

            logger.info(f"Fetched {len(results)} cost records")
            return results

        except ClientError as error:
            logger.error(f"AWS Cost Explorer ClientError: {error}")
            return {
                "error": True,
                "type": "AWS_CLIENT_ERROR",
                "message": str(error)
            }

        except BotoCoreError as error:
            logger.error(f"AWS BotoCoreError: {error}")
            return {
                "error": True,
                "type": "AWS_BOTOCORE_ERROR",
                "message": str(error)
            }

        except Exception as error:
            logger.exception("Unexpected error while fetching cost data")
            return {
                "error": True,
                "type": "UNEXPECTED_ERROR",
                "message": str(error)
            }
