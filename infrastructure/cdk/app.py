#!/usr/bin/env python3

import aws_cdk as cdk

from finops_execution_stack import FinOpsExecutionStack
from cognito_stack import CognitoAuthStack

app = cdk.App()

env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region="us-east-1"
)

FinOpsExecutionStack(
    app,
    "FinOpsExecutionStack",
    env=env
)

CognitoAuthStack(
    app,
    "CognitoAuthStack",
    env=env
)

app.synth()
