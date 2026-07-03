from botocore.exceptions import ClientError, BotoCoreError

from backend.core.base_tool import BaseTool
from backend.services.aws_session_manager import AWSSessionManager
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class OrganizationsTool(BaseTool):
    name = "organizations"

    def __init__(self):
        session = AWSSessionManager.get_session()
        self.client = session.client(
            "organizations",
            region_name="us-east-1"
        )

    def execute(self):
        try:
            paginator = self.client.get_paginator("list_accounts")

            accounts = []

            for page in paginator.paginate():
                for account in page.get("Accounts", []):
                    accounts.append({
                        "account_id": account.get("Id"),
                        "name": account.get("Name"),
                        "email": account.get("Email"),
                        "status": account.get("Status"),
                        "joined_method": account.get("JoinedMethod"),
                        "joined_timestamp": (
                            account.get("JoinedTimestamp").isoformat()
                            if account.get("JoinedTimestamp")
                            else None
                        )
                    })

            return self.success_response({
                "accounts_found": len(accounts),
                "accounts": accounts
            })

        except ClientError as error:
            logger.error(f"Organizations ClientError: {error}")
            return self.error_response("AWS_CLIENT_ERROR", str(error))

        except BotoCoreError as error:
            logger.error(f"Organizations BotoCoreError: {error}")
            return self.error_response("AWS_BOTOCORE_ERROR", str(error))

        except Exception as error:
            logger.exception("Unexpected Organizations Tool error")
            return self.error_response("UNEXPECTED_ERROR", str(error))

