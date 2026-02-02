import json
import boto3
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# Warm-start: Loaded once when the container starts
MODEL_PATH = "/var/task/mxbai_model"
model = SentenceTransformer(MODEL_PATH, device="cpu")

# model = SentenceTransformer(
#     "mixedbread-ai/mxbai-embed-large-v1",
#     device="cuda"
# )

"""
docker run -p 9000:8080 \
  -e QDRANT_URL="$(grep QDRANT_URL ../../.env | cut -d '=' -f2 | xargs)" \
  -e QDRANT_API_KEY="$(grep QDRANT_API_KEY ../../.env | cut -d '=' -f2 | xargs)" \
  -e AWS_ACCESS_KEY_ID="$(aws configure get aws_access_key_id)" \
  -e AWS_SECRET_ACCESS_KEY="$(aws configure get aws_secret_access_key)" \
  -e AWS_REGION="us-east-1" \
  lenny-agent

"""

# Clients
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

qdrant = QdrantClient(url=os.environ['QDRANT_URL'], api_key=os.environ['QDRANT_API_KEY'] , port=None) # because : https://github.com/qdrant/qdrant-client/issues/394#issuecomment-2075283788

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']

    domain = event['requestContext']['domainName']
    stage = event['requestContext']['stage']
    apigw = boto3.client('apigatewaymanagementapi', endpoint_url=f"https://{domain}/{stage}" , region_name='us-east-1')

    try:
        # 1. Parse User Query
        body = json.loads(event.get('body', '{}'))
        user_query = body.get('message', '')
        print(f" USER QUERY: {user_query}")

        # 2. RAG: Embedding
        print(" STEP 1: Encoding query into vector...")
        query_vector = model.encode(user_query).tolist()
        print("SUCCESS: Vector generated.")


        search_result = qdrant.query_points(
            collection_name="virtual-lenny",
            query=query_vector,
            limit=3,
            timeout=10
        )
        results = search_result.points # https://github.com/qdrant/qdrant-client
        print(f"SUCCESS: Qdrant returned {len(results)} points.")


        context_text = "\n\n".join([r.payload['content'] for r in results])
        print("--- CONTEXT FOUND ---")
        print(context_text)
        print("----------------------")

    #     context_text = "\n\n".join([r.payload['content'] for r in results])

    #     print(context_text)
    #     # 3. Prompt Construction
    #     prompt = f"""You are Lenny Rachitsky. Use the context below to answer.
    #     Context: {context_text}
    #     Question: {user_query}
    #     Answer:"""

    #     # https://docs.aws.amazon.com/code-library/latest/ug/python_3_bedrock-runtime_code_examples.html 
    #     # 4. Bedrock Streaming 
    #     response = bedrock.converse_stream(
    #                 modelId="amazon.nova-lite-v1:0",
    #                 messages=[{
    #                     "role": "user",
    #                     "content": [{"text": prompt}]
    #                 }],
    #                 inferenceConfig={"maxTokens": 512, "temperature": 0.5}
    #             )

    #     # 5. Token Streaming Loop for ConverseStream
    #     # ConverseStream uses different event types than the native Claude API
    #     for event in response.get("stream"):
    #         # 'contentBlockDelta' is where the actual text tokens live
    #         if "contentBlockDelta" in event:
    #             token = event["contentBlockDelta"]["delta"]["text"]
                
    #             # Push the token to the WebSocket
    #             apigw.post_to_connection(
    #                 ConnectionId=connection_id, 
    #                 Data=json.dumps({"type": "chunk", "content": token})
    #             )

    #     # Signal completion
    #     apigw.post_to_connection(ConnectionId=connection_id, Data=json.dumps({"type": "done"}))

    except Exception as e:
        print(f"Error: {str(e)}")
        apigw.post_to_connection(ConnectionId=connection_id, Data=json.dumps({"type": "error", "message": str(e)}))

    return {'statusCode': 200}