import json
import boto3
from langchain_text_splitters import RecursiveCharacterTextSplitter

s3 = boto3.client('s3')

# Initialize splitter
yt_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)

def lambda_handler(event, context):
    """
    Chunk cleaned data and save to S3.
    
    Expected event:
    {
        "input_bucket": "virtual-lenny-bucket",
        "input_prefixes":  ["data/processed/linkedin/", "data/processed/youtube/"] ,
        "output_bucket": "virtual-lenny-bucket",
        "output_key": "data/chunks/final_chunks.json"
    }
    """
    try:
    
        # Check if output already exists
        try:
            s3.head_object(Bucket=event['output_bucket'], Key=event['output_key'])
            print(f"SKIPPING: {event['output_key']} already exists")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'total_chunks': 0,
                    'message': "Output already exists"
                })
            }
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] != '404':
                raise

        all_chunks = []
        
        # Process each source
        for prefix in event['input_prefixes']:
            source = 'linkedin' if 'linkedin' in prefix else 'youtube'
            
            # List files
            response = s3.list_objects_v2(
                Bucket=event['input_bucket'],
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                continue
            
            print(f"Processing {len(response['Contents'])} {source} files")
            
            for obj in response['Contents']:
                key = obj['Key']
                
                if not key.endswith('.json'):
                    continue
                
                # Read file
                file_data = s3.get_object(
                    Bucket=event['input_bucket'],
                    Key=key
                )
                data = json.loads(file_data['Body'].read())
                
                text = data.get("text", "")
                if not text:
                    continue
                
                # Chunk based on source
                if source == "linkedin":
                    # Keep LinkedIn posts as single chunks
                    chunk_data = {
                        "chunk_id": f"li_{data.get('post_id')}",
                        "source": "linkedin",
                        "content": text,
                        "metadata": {
                            "url": data.get("url"),
                            "author": data.get("author", "Lenny Rachitsky")
                        }
                    }
                    all_chunks.append(chunk_data)
                    
                elif source == "youtube":
                    # Split YouTube transcripts
                    chunks = yt_splitter.split_text(text)
                    for i, chunk_text in enumerate(chunks):
                        chunk_data = {
                            "chunk_id": f"yt_{data.get('video_id')}_{i}",
                            "source": "youtube",
                            "content": chunk_text,
                            "metadata": {
                                "url": data.get("url"),
                                "author": "Lenny Rachitsky",
                                "chunk_index": i
                            }
                        }
                        all_chunks.append(chunk_data)
        
        # Save all chunks to S3
        s3.put_object(
            Bucket=event['output_bucket'],
            Key=event['output_key'],
            Body=json.dumps(all_chunks, indent=2),
            ContentType='application/json'
        )
        
        print(f"Created {len(all_chunks)} total chunks")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'total_chunks': len(all_chunks),
                'output_location': f"s3://{event['output_bucket']}/{event['output_key']}"
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }