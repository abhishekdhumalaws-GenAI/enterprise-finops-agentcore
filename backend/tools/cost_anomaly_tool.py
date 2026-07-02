from datetime import date, timedelta

from botocore.exceptions import BotoCoreError, ClientError

from backend.config.settings import settings
from backend.core.base_tool import BaseTool
from backend.services.aws_session_manager import AWSSessionManager
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class CostAnomalyTool(BaseTool):
    name = "cost_anomaly"

    def __init__(self):
        session = AWSSessionManager.get_session()
        self.client = session.client(
            "ce",
            region_name=settings.AWS_REGION
        )

    def execute(self, days: int = 30):
        try:
            if days > 90:
                days = 90

            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            logger.info(f"Fetching cost anomalies for last {days} days")

            response = self.client.get_anomalies(
                DateInterval={
                    "StartDate": start_date.isoformat(),
                    "EndDate": end_date.isoformat()
                },
                MaxResults=20
            )

            anomalies = []

            for item in response.get("Anomalies", []):
                impact = item.get("Impact", {})

                anomalies.append({
                    "anomaly_id": item.get("AnomalyId"),
                    "start_date": item.get("AnomalyStartDate"),
                    "end_date": item.get("AnomalyEndDate"),
                    "dimension_value": item.get("DimensionValue"),
                    "root_causes": item.get("RootCauses", []),
                    "total_impact": impact.get("TotalImpact"),
                    "total_actual_spend": impact.get("TotalActualSpend"),
                    "total_expected_spend": impact.get("TotalExpectedSpend"),
                    "percentage_impact": impact.get("TotalImpactPercentage")
                })

            return self.success_response(anomalies)

        except ClientError as error:
            logger.error(f"Cost Anomaly ClientError: {error}")
            return self.error_response("AWS_CLIENT_ERROR", str(error))

        except BotoCoreError as error:
            logger.error(f"Cost Anomaly BotoCoreError: {error}")
            return self.error_response("AWS_BOTOCORE_ERROR", str(error))

        except Exception as error:
            logger.exception("Unexpected Cost Anomaly error")
            return self.error_response("UNEXPECTED_ERROR", str(error))
