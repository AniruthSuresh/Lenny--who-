from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct
import os

class WebSocketStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        
        # 1. DynamoDB for Connection Tracking
        connections_table = dynamodb.Table(
            self, "ConnectionsTable",
            partition_key=dynamodb.Attribute(name="connectionId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            table_name="virtual-lenny-connections"
        )
        
        # 2. Connection Handlers (Simple Python Functions)
        connect_handler = _lambda.Function(
            self, "ConnectHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../../agent/connect_handler"),
            environment={"CONNECTIONS_TABLE": connections_table.table_name}
        )
        
        disconnect_handler = _lambda.Function(
            self, "DisconnectHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../agent/disconnect_handler"),
            environment={"CONNECTIONS_TABLE": connections_table.table_name}
        )
        
        connections_table.grant_read_write_data(connect_handler)
        connections_table.grant_read_write_data(disconnect_handler)
        
        # 3. Message Handler (Your Verified Docker Lambda)
        message_handler = _lambda.DockerImageFunction(
            self, "MessageHandler",
            code=_lambda.DockerImageCode.from_image_asset("../agent/message_handler"),
            timeout=Duration.minutes(2),
            memory_size=3008,
            environment={
                "QDRANT_URL": os.getenv("QDRANT_URL", ""),
                "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY", ""),
            }
        )
        
        # Grant Bedrock Permissions
        message_handler.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:ConverseStream", "bedrock:InvokeModel"],
            resources=["*"]
        ))
        
        # 4. WebSocket API Setup
        web_socket_api = apigwv2.WebSocketApi(
            self, "VirtualLennyWebSocket",
            connect_route_options=apigwv2.WebSocketRouteOptions(
                integration=integrations.WebSocketLambdaIntegration("ConnIn", connect_handler)
            ),
            disconnect_route_options=apigwv2.WebSocketRouteOptions(
                integration=integrations.WebSocketLambdaIntegration("DiscIn", disconnect_handler)
            ),
            default_route_options=apigwv2.WebSocketRouteOptions(
                integration=integrations.WebSocketLambdaIntegration("MsgIn", message_handler)
            )
        )
        
        stage = apigwv2.WebSocketStage(
            self, "Prod", 
            web_socket_api=web_socket_api, 
            stage_name="prod", 
            auto_deploy=True
        )
        
        # Crucial for post_to_connection
        web_socket_api.grant_manage_connections(message_handler)

        CfnOutput(self, "WebSocketURL", value=stage.url)