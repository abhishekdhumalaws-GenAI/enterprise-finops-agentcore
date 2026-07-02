import boto3

from backend.config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AWSSessionManager:
    @staticmethod
    def get_session():
        if settings.AWS_PROFILE:
            logger.info(f"Using AWS profile: {settings.AWS_PROFILE}")
            return boto3.Session(profile_name=settings.AWS_PROFILE)

        logger.info("Using default AWS credential chain")
        return boto3.Session()
