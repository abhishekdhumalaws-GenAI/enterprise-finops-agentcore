from botocore.exceptions import ClientError, BotoCoreError

from backend.config.settings import settings
from backend.core.base_tool import BaseTool
from backend.services.aws_session_manager import AWSSessionManager
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class EC2DiscoveryTool(BaseTool):
    name = "ec2_discovery"

    def __init__(self):
        session = AWSSessionManager.get_session()
        self.client = session.client(
            "ec2",
            region_name=settings.AWS_REGION
        )

    def execute(self, instance_type: str | None = None):
        try:
            filters = [
                {
                    "Name": "instance-state-name",
                    "Values": ["pending", "running", "stopping", "stopped"]
                }
            ]

            if instance_type:
                filters.append({
                    "Name": "instance-type",
                    "Values": [instance_type]
                })

            response = self.client.describe_instances(
                Filters=filters
            )

            instances = []

            for reservation in response.get("Reservations", []):
                for item in reservation.get("Instances", []):
                    name = None

                    for tag in item.get("Tags", []):
                        if tag.get("Key") == "Name":
                            name = tag.get("Value")

                    instances.append({
                        "instance_id": item.get("InstanceId"),
                        "instance_type": item.get("InstanceType"),
                        "state": item.get("State", {}).get("Name"),
                        "availability_zone": item.get("Placement", {}).get("AvailabilityZone"),
                        "private_ip": item.get("PrivateIpAddress"),
                        "public_ip": item.get("PublicIpAddress"),
                        "name": name,
                        "launch_time": item.get("LaunchTime").isoformat()
                        if item.get("LaunchTime")
                        else None
                    })

            return self.success_response({
                "instance_type_filter": instance_type,
                "instances_found": len(instances),
                "instances": instances
            })

        except ClientError as error:
            logger.error(f"EC2 Discovery ClientError: {error}")
            return self.error_response("AWS_CLIENT_ERROR", str(error))

        except BotoCoreError as error:
            logger.error(f"EC2 Discovery BotoCoreError: {error}")
            return self.error_response("AWS_BOTOCORE_ERROR", str(error))

        except Exception as error:
            logger.exception("Unexpected EC2 Discovery error")
            return self.error_response("UNEXPECTED_ERROR", str(error))
