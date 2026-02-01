import os
import json
from dotenv import load_dotenv
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from lambdas.chunk_data.handler import lambda_handler 

load_dotenv()

def test_chunk_lambda():
    class MockContext:
        def __init__(self):
            self.aws_request_id = "test-request-id-123"

    test_event = {
        "input_bucket": "virtual-lenny-bucket",
        "input_prefixes": ["data/processed/linkedin/", "data/processed/youtube/"],
        "output_bucket": "virtual-lenny-bucket",
        "output_key":  "data/chunks/final_chunks.json"
    }

    print("Starting Local Lambda Test...")

    response = lambda_handler(test_event, MockContext())
    status_code = response['statusCode']
    body = json.loads(response['body'])

    if status_code == 200:
        if body.get("total_chunks") == 0:
            print("Output already exists, skipped.")
        else:
            print(f"SUCCESS! Total chunks created: {body['total_chunks']}")
            print(f"Location: {body['output_location']}")
    else:
        print("FAILED!")
        print(f"Error: {body.get('error')}")

if __name__ == "__main__":
    if not os.getenv("DATA_BUCKET_NAME"):
        print(" Error: DATA_BUCKET_NAME not found in environment.")
    else:
        test_chunk_lambda()