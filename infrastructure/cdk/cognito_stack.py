from aws_cdk import (
    CfnOutput,
    Stack,
    aws_cognito as cognito,
)
from constructs import Construct


class CognitoAuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        user_pool = cognito.UserPool(
            self,
            "FinOpsUserPool",
            user_pool_name="enterprise-finops-user-pool",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(
                email=True
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
        )

        app_client = cognito.UserPoolClient(
            self,
            "FinOpsUserPoolClient",
            user_pool=user_pool,
            user_pool_client_name="enterprise-finops-app-client",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
            generate_secret=False,
        )

        cognito.CfnUserPoolGroup(
            self,
            "ViewerGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="Viewer",
            description="Read-only dashboard users",
        )

        cognito.CfnUserPoolGroup(
            self,
            "ApproverGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="Approver",
            description="Users allowed to approve FinOps recommendations",
        )

        cognito.CfnUserPoolGroup(
            self,
            "AdminGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="Admin",
            description="Platform administrators",
        )

        CfnOutput(
            self,
            "FinOpsUserPoolId",
            value=user_pool.user_pool_id,
        )

        CfnOutput(
            self,
            "FinOpsUserPoolClientId",
            value=app_client.user_pool_client_id,
        )
