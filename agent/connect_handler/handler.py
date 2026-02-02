import boto3
import os
import json 

DYNAMODB = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        table_name = os.environ.get('CONNECTIONS_TABLE')
        if not table_name:
            raise ValueError("CONNECTIONS_TABLE environment variable is not set")
            
        table = DYNAMODB.Table(table_name)
        
        connection_id = event.get('requestContext', {}).get('connectionId')
        if not connection_id:
            raise ValueError("No connectionId found in requestContext")

        print(f"Attempting to connect: {connection_id}")

        table.put_item(Item={
            'connectionId': connection_id,
            'connectedAt': str(context.aws_request_id) 
        })
        
        print(f"Connection successful: {connection_id}")
    
        return {
            'statusCode': 200,
            'body': 'Connected'
        }
        
    except Exception as e:
        print(f" CRITICAL ERROR in ConnectHandler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }