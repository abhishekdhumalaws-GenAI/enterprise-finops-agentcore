#!/usr/bin/env python3

import aws_cdk as cdk
from finops_execution_stack import FinOpsExecutionStack

app = cdk.App()

FinOpsExecutionStack(
    app,
    "FinOpsExecutionStack",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region="us-east-1"
    )
)

app.synth()
