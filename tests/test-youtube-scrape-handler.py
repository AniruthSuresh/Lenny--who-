import os
import json
from dotenv import load_dotenv
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
from lambdas.scrape_youtube.handler import lambda_handler 

load_dotenv()  #

def test_youtube_lambda():
    class MockContext:
        def __init__(self):
            self.aws_request_id = "test-request-id-123"

    # ----------------------------
    # Build the event for Lambda
    # ----------------------------
    test_event = {
        "input_bucket": os.getenv("DATA_BUCKET_NAME"),   
        "video_ids_key": "data/raw/youtube/video_ids.txt",
        "output_bucket": os.getenv("DATA_BUCKET_NAME"),
        "output_prefix": "data/raw/youtube/transcripts/"
    }

    print("Starting Local Lambda Test...")

    response = lambda_handler(test_event, MockContext())

    # Parse the response
    status_code = response['statusCode']
    body = json.loads(response['body'])

    if status_code == 200:
        print("SUCCESS!")
        print(f"Videos Processed: {body['videos_processed']} / {body['total_videos']}")
    else:
        print("FAILED!")
        print(f"Error: {body.get('error')}")

if __name__ == "__main__":

    if not os.getenv("ACCESS_KEY") or not os.getenv("SECRET_ACCESS_KEY"):
        print("Error: AWS credentials not found in environment.")
    elif not os.getenv("DATA_BUCKET_NAME"):
        print("Error: DATA_BUCKET_NAME not set in environment.")

    else:
        test_youtube_lambda()
