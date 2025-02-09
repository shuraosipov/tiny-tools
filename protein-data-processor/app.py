#!/usr/bin/env python3
from aws_cdk import (
    App,
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_s3_notifications as s3n,
)
from constructs import Construct

class ProteinProcessorStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket for protein data
        bucket = s3.Bucket(self, "XXXXXXXXXXXXXXXXXXXXX",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True)

        # Create a DynamoDB table to store processed data
        table = dynamodb.Table(
            self,
            "ProteinTable",
            partition_key=dynamodb.Attribute(
                name="protein_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sequence_type",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Create Lambda function
        lambda_fn = _lambda.Function(
            self,
            "ProteinProcessor",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="handler.lambda_handler",
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "DYNAMODB_TABLE": table.table_name
            }
        )

        # Grant Lambda permissions
        bucket.grant_read(lambda_fn)
        table.grant_write_data(lambda_fn)

        # Add S3 notification to trigger Lambda
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(lambda_fn)
        )

app = App()
ProteinProcessorStack(app, "ProteinProcessorStack")
app.synth()