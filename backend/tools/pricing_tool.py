import json

from botocore.exceptions import ClientError, BotoCoreError

from backend.config.settings import settings
from backend.core.base_tool import BaseTool
from backend.services.aws_session_manager import AWSSessionManager
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PricingTool(BaseTool):
    name = "pricing"

    def __init__(self):
        session = AWSSessionManager.get_session()

        # AWS Pricing API endpoint is not tied to workload region.
        self.client = session.client(
            "pricing",
            region_name="us-east-1"
        )

    def execute(self, service: str = "EC2", region_name: str = "US East (N. Virginia)", instance_type: str = "g5.xlarge"):
        try:
            if service == "EC2":
                return self.get_ec2_ondemand_price(
                    region_name=region_name,
                    instance_type=instance_type
                )

            return self.error_response(
                "UNSUPPORTED_SERVICE",
                f"Pricing lookup is not implemented yet for service: {service}"
            )

        except ClientError as error:
            logger.error(f"Pricing ClientError: {error}")
            return self.error_response("AWS_CLIENT_ERROR", str(error))

        except BotoCoreError as error:
            logger.error(f"Pricing BotoCoreError: {error}")
            return self.error_response("AWS_BOTOCORE_ERROR", str(error))

        except Exception as error:
            logger.exception("Unexpected Pricing Tool error")
            return self.error_response("UNEXPECTED_ERROR", str(error))

    def get_ec2_ondemand_price(self, region_name: str, instance_type: str):
        logger.info(
            f"Fetching EC2 On-Demand pricing | region={region_name}, instance={instance_type}"
        )

        response = self.client.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {
                    "Type": "TERM_MATCH",
                    "Field": "instanceType",
                    "Value": instance_type
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "location",
                    "Value": region_name
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "operatingSystem",
                    "Value": "Linux"
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "tenancy",
                    "Value": "Shared"
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "preInstalledSw",
                    "Value": "NA"
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "capacitystatus",
                    "Value": "Used"
                }
            ],
            FormatVersion="aws_v1",
            MaxResults=1
        )

        price_list = response.get("PriceList", [])

        if not price_list:
            return self.success_response({
                "service": "EC2",
                "region": region_name,
                "instance_type": instance_type,
                "price_found": False,
                "message": "No matching EC2 price found."
            })

        product = json.loads(price_list[0])

        product_attributes = product.get("product", {}).get("attributes", {})
        terms = product.get("terms", {}).get("OnDemand", {})

        price_per_hour = None
        unit = None
        description = None

        for term in terms.values():
            price_dimensions = term.get("priceDimensions", {})

            for dimension in price_dimensions.values():
                price_per_hour = dimension.get("pricePerUnit", {}).get("USD")
                unit = dimension.get("unit")
                description = dimension.get("description")
                break

            if price_per_hour is not None:
                break

        return self.success_response({
            "service": "EC2",
            "region": region_name,
            "instance_type": instance_type,
            "operating_system": "Linux",
            "tenancy": "Shared",
            "price_found": True,
            "price_per_hour_usd": float(price_per_hour) if price_per_hour else None,
            "unit": unit,
            "description": description,
            "attributes": {
                "vcpu": product_attributes.get("vcpu"),
                "memory": product_attributes.get("memory"),
                "network_performance": product_attributes.get("networkPerformance"),
                "processor": product_attributes.get("physicalProcessor")
            }
        })
