import boto3, os
table = boto3.resource('dynamodb').Table(os.environ['CONNECTIONS_TABLE'])

def lambda_handler(event, context):
    table.delete_item(Key={'connectionId': event['requestContext']['connectionId']})
    return {'statusCode': 200}

