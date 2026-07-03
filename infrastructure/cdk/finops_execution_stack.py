from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_stepfunctions as sfn,
)
from constructs import Construct


class FinOpsExecutionStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        precheck = sfn.Pass(
            self,
            "PreCheck",
            result=sfn.Result.from_object({
                "stage": "precheck",
                "status": "PASSED",
                "message": "Dry-run precheck completed."
            }),
            result_path="$.precheck"
        )

        execute = sfn.Pass(
            self,
            "ExecuteChange",
            result=sfn.Result.from_object({
                "stage": "execution",
                "status": "SIMULATED_SUCCESS",
                "message": "Dry-run execution completed. No AWS resource was modified."
            }),
            result_path="$.execution"
        )

        verify = sfn.Pass(
            self,
            "VerifyChange",
            result=sfn.Result.from_object({
                "stage": "verification",
                "status": "PASSED",
                "rollback_required": False
            }),
            result_path="$.verification"
        )

        prepare_rollback = sfn.Pass(
            self,
            "PrepareRollback",
            result=sfn.Result.from_object({
                "stage": "rollback",
                "status": "READY",
                "message": "Rollback plan prepared."
            }),
            result_path="$.rollback"
        )

        complete = sfn.Succeed(
            self,
            "Complete"
        )

        complete_with_rollback = sfn.Succeed(
            self,
            "CompleteWithRollback"
        )

        rollback_decision = sfn.Choice(
            self,
            "RollbackDecision"
        )

        definition = (
            precheck
            .next(execute)
            .next(verify)
            .next(
                rollback_decision
                .when(
                    sfn.Condition.boolean_equals(
                        "$.verification.rollback_required",
                        True
                    ),
                    prepare_rollback.next(complete_with_rollback)
                )
                .otherwise(complete)
            )
        )

        state_machine = sfn.StateMachine(
            self,
            "FinOpsExecutionWorkflow",
            state_machine_name="enterprise-finops-execution-workflow",
            definition_body=sfn.DefinitionBody.from_chainable(definition),
            timeout=Duration.minutes(15)
        )

        CfnOutput(
            self,
            "FinOpsStateMachineArn",
            value=state_machine.state_machine_arn
        )
