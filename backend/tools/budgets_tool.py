from botocore.exceptions import ClientError, BotoCoreError

from backend.config.settings import settings
from backend.core.base_tool import BaseTool
from backend.services.aws_session_manager import AWSSessionManager
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class BudgetsTool(BaseTool):
    name = "budgets"

    def __init__(self):
        session = AWSSessionManager.get_session()
        self.client = session.client(
            "budgets",
            region_name="us-east-1"
        )
        self.sts_client = session.client(
            "sts",
            region_name=settings.AWS_REGION
        )

    def execute(self):
        try:
            account_id = self.sts_client.get_caller_identity()["Account"]

            response = self.client.describe_budgets(
                AccountId=account_id,
                MaxResults=20
            )

            budgets = []

            for item in response.get("Budgets", []):
                calculated = item.get("CalculatedSpend", {})
                actual = calculated.get("ActualSpend", {})
                forecasted = calculated.get("ForecastedSpend", {})
                limit = item.get("BudgetLimit", {})

                budgets.append({
                    "budget_name": item.get("BudgetName"),
                    "budget_type": item.get("BudgetType"),
                    "time_unit": item.get("TimeUnit"),
                    "limit_amount": float(limit.get("Amount", 0)),
                    "limit_unit": limit.get("Unit"),
                    "actual_spend": float(actual.get("Amount", 0)),
                    "actual_unit": actual.get("Unit"),
                    "forecasted_spend": float(forecasted.get("Amount", 0)),
                    "forecasted_unit": forecasted.get("Unit")
                })

            return self.success_response({
                "account_id": account_id,
                "budgets_found": len(budgets),
                "budgets": budgets
            })

        except ClientError as error:
            logger.error(f"Budgets ClientError: {error}")
            return self.error_response("AWS_CLIENT_ERROR", str(error))

        except BotoCoreError as error:
            logger.error(f"Budgets BotoCoreError: {error}")
            return self.error_response("AWS_BOTOCORE_ERROR", str(error))

        except Exception as error:
            logger.exception("Unexpected Budgets Tool error")
            return self.error_response("UNEXPECTED_ERROR", str(error))
