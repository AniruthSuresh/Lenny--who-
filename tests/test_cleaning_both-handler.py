import os
import json
import sys
from dotenv import load_dotenv

# Make sure your project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# Import your Lambda handler
from lambdas.clean_data.handler import lambda_handler

load_dotenv()  # Load environment variables from .env

def test_clean_data_lambda():

    class MockContext:
        def __init__(self):
            self.aws_request_id = "test-request-id-123"

    # --- Define your test event ---
    # Make sure these buckets/prefixes exist and have some JSON files for testing
    test_event = {
        "input_bucket": os.getenv("DATA_BUCKET_NAME"),  # e.g., "virtual-lenny-bucket"
        "input_prefixes": [
            "data/raw/linkedin/",
            "data/raw/youtube/transcripts/"
        ],
        "output_bucket": os.getenv("DATA_BUCKET_NAME"),  # same bucket for output
        "output_prefixes": [
            "data/processed/linkedin/",
            "data/processed/youtube/"
        ]
    }

    print(" Starting Local Lambda Test for Cleaning Data...")
    
    response = lambda_handler(test_event, MockContext())

    status_code = response['statusCode']
    body = json.loads(response['body'])

    if status_code == 200:
        print(" SUCCESS!")
        print(f" Files Cleaned: {body['files_cleaned']}")
    else:
        print(" FAILED!")
        print(f"Error: {body.get('error')}")

if __name__ == "__main__":
    if not os.getenv("DATA_BUCKET_NAME"):
        print(" Error: DATA_BUCKET_NAME not found in environment.")
    else:
        test_clean_data_lambda()