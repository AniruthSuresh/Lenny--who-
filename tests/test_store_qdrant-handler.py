import os
import json
import sys
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from lambdas.store_qdrant.handler import lambda_handler

load_dotenv()

def test_store_qdrant_cloud():
    """
    Test the Qdrant Cloud storage Lambda locally.
    
    Prerequisites:
    1. Qdrant Cloud account with cluster URL and API key
    2. Embeddings file must exist in S3
    3. Environment variables set:
       - DATA_BUCKET_NAME
       - QDRANT_URL (your Qdrant Cloud URL)
       - QDRANT_API_KEY (your Qdrant Cloud API key)
    """
    
    class MockContext:
        def __init__(self):
            self.aws_request_id = "test-request-id-123"
            self.function_name = "test-store-qdrant"
    
    required_vars = {
        "DATA_BUCKET_NAME": os.getenv("DATA_BUCKET_NAME"),
        "QDRANT_URL": os.getenv("QDRANT_URL"),
        "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY")
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        print(" Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file:")
        print("DATA_BUCKET_NAME=virtual-lenny-bucket")
        print("QDRANT_URL=https://your-cluster.aws.cloud.qdrant.io")
        print("QDRANT_API_KEY=your-api-key-here")
        return
    
    test_event = {
        "input_bucket": os.getenv("DATA_BUCKET_NAME"),
        "embeddings_key": "data/embedded/mxbai_corpus.pt",
        "collection_name": "virtual-lenny",
        "qdrant_url": os.getenv("QDRANT_URL"),
        "qdrant_api_key": os.getenv("QDRANT_API_KEY"),
        "recreate_collection": False, 
        "batch_size": 100 
    }
    
    print("=" * 70)
    print("🧪 TESTING QDRANT CLOUD STORAGE LAMBDA")
    print("=" * 70)
    print(f"Qdrant URL: {test_event['qdrant_url']}")
    print(f" S3 Bucket: {test_event['input_bucket']}")
    print(f" Embeddings: {test_event['embeddings_key']}")
    print(f"  Collection: {test_event['collection_name']}")
    print(f" Recreate: {test_event['recreate_collection']}")
    print(f" Batch Size: {test_event['batch_size']}")
    print("=" * 70)
    print()
    
    print(" Starting Lambda execution...\n")
    
    try:
        response = lambda_handler(test_event, MockContext())
        
        status_code = response['statusCode']
        body = json.loads(response['body'])
        
        print("\n" + "=" * 70)
        print(" LAMBDA EXECUTION RESULT")
        print("=" * 70)
        
        if status_code == 200:
            print(" STATUS: SUCCESS")
            print()
            
            if body.get('skipped'):
                print(" RESULT: Skipped (collection already exists)")
                print(f" Existing Points: {body.get('existing_points')}")
            else:
                print(" RESULT: Upload Complete")
                print(f" Vectors Uploaded: {body.get('vectors_uploaded')}")
                print(f" Total Points in Collection: {body.get('collection_points_count')}")
            
            print(f"  Collection Name: {body.get('collection_name')}")
            print(f" Qdrant URL: {body.get('qdrant_url')}")
            
            print()
            print("=" * 70)
            print(" TEST PASSED")
            print("=" * 70)
            
            # Provide next steps
            print("\n NEXT STEPS:")
            print("1. Verify in Qdrant Cloud dashboard")
            print(f"   URL: {test_event['qdrant_url'].replace('//', '//console.')}")
            print("2. Test a sample query:")
            print(f"   Collection: {test_event['collection_name']}")
            print("3. Proceed to Phase 2 (WebSocket + RAG Agent)")
            
        else:
            print(" STATUS: FAILED")
            print(f" Error: {body.get('error')}")
            print()
            print("=" * 70)
            print(" TEST FAILED")
            print("=" * 70)
            
            # Troubleshooting tips
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Check Qdrant Cloud credentials")
            print("2. Verify S3 embeddings file exists")
            print("3. Check Lambda logs above for details")
            print("4. Ensure Qdrant cluster is running")
    
    except Exception as e:
        print(f"\n EXCEPTION DURING TEST: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        print("=" * 70)
        print(" TEST FAILED WITH EXCEPTION")
        print("=" * 70)

def verify_s3_file_exists():
    """Helper to check if embeddings file exists in S3"""
    import boto3
    
    bucket = os.getenv("DATA_BUCKET_NAME")
    key = "data/embeddings/mxbai_corpus.pt"
    
    if not bucket:
        print("  Cannot verify - DATA_BUCKET_NAME not set")
        return
    
    try:
        s3 = boto3.client('s3')
        s3.head_object(Bucket=bucket, Key=key)
        print(f" Embeddings file exists: s3://{bucket}/{key}")
    except Exception as e:
        print(f" Embeddings file not found: s3://{bucket}/{key}")
        print(f"   Error: {str(e)}")
        print("\n TIP: Run the embedding generation Lambda first")

if __name__ == "__main__":
    print("\n Pre-flight checks...\n")
    
    # Verify S3 file
    verify_s3_file_exists()
    
    print()
    
    # Run test
    test_store_qdrant_cloud()