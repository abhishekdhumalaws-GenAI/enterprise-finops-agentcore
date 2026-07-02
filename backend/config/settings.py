import os


class Settings:
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_PROFILE = os.getenv("AWS_PROFILE")
    COST_METRIC = os.getenv("COST_METRIC", "UnblendedCost")
    APP_NAME = os.getenv("APP_NAME", "Enterprise FinOps AgentCore API")
    BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0")


settings = Settings()
