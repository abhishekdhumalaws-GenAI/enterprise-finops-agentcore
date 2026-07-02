from botocore.exceptions import ClientError, BotoCoreError

from backend.config.settings import settings
from backend.core.base_tool import BaseTool
from backend.services.aws_session_manager import AWSSessionManager
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class CURTool(BaseTool):
    name = "cur"

    def __init__(self):
        session = AWSSessionManager.get_session()
        self.client = session.client(
            "cur",
            region_name="us-east-1"
        )

    def execute(self):
        try:
            response = self.client.describe_report_definitions()

            reports = []

            for item in response.get("ReportDefinitions", []):
                reports.append({
                    "report_name": item.get("ReportName"),
                    "time_unit": item.get("TimeUnit"),
                    "format": item.get("Format"),
                    "compression": item.get("Compression"),
                    "s3_bucket": item.get("S3Bucket"),
                    "s3_prefix": item.get("S3Prefix"),
                    "s3_region": item.get("S3Region"),
                    "additional_schema_elements": item.get("AdditionalSchemaElements", []),
                    "refresh_closed_reports": item.get("RefreshClosedReports"),
                    "report_versioning": item.get("ReportVersioning")
                })

            return self.success_response({
                "cur_reports_found": len(reports),
                "reports": reports
            })

        except ClientError as error:
            logger.error(f"CUR ClientError: {error}")
            return self.error_response("AWS_CLIENT_ERROR", str(error))

        except BotoCoreError as error:
            logger.error(f"CUR BotoCoreError: {error}")
            return self.error_response("AWS_BOTOCORE_ERROR", str(error))

        except Exception as error:
            logger.exception("Unexpected CUR Tool error")
            return self.error_response("UNEXPECTED_ERROR", str(error))
