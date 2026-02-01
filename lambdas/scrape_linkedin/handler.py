import json
import boto3
import os
from apify_client import ApifyClient
from typing import List, Dict

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Scrape LinkedIn posts and save to S3.
    
    Expected event:
    {
        "profile_url": "https://linkedin.com/in/lennyrachitsky",
        "count": 100,
        "output_bucket": "lenny-rag-data",
        "output_prefix": "raw/linkedin/"
    }
    """
    try:
        # Parse input
        profile_url = event['profile_url']
        count = event.get('count', 100)
        bucket = event['output_bucket']
        prefix = event['output_prefix']
        
        # Scrape posts
        print(f"Scraping {count} posts from {profile_url}")
        items = scrape_linkedin_posts(profile_url, count)
        
        # Save to S3
        saved_count = 0
        for item in items:
            key = f"{prefix}{item['post_id']}.json"
            try:
                s3.head_object(Bucket=bucket, Key=key)
                print(f" Post {item['post_id']} already exists in S3, skipping.")
                continue 
            except s3.exceptions.ClientError:

                s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=json.dumps(item, indent=2),
                    ContentType='application/json'
                )
                saved_count += 1
        
        print(f"Successfully saved {saved_count} posts to S3")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'posts_scraped': saved_count,
                'output_location': f"s3://{bucket}/{prefix}"
            })
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def scrape_linkedin_posts(profile_url: str, count: int) -> List[Dict]:
    """
    Scrape LinkedIn posts using Apify.
    
    This is your existing logic, adapted to use environment variables.
    """
    apify_token = os.environ['APIFY_TOKEN']
    client = ApifyClient(apify_token)
    
    run_input = {
        "profileUrl": profile_url,
        "username": profile_url.split("/")[-2],
        "count": count,
        "limit": count
    }
    
    print(f"Triggering Apify actor...")
    run = client.actor("apimaestro/linkedin-profile-posts").call(run_input=run_input)
    
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"Found {len(items)} raw items in dataset")
    
    # Process items (your existing logic)
    processed_items = []
    for index, item in enumerate(items):
        # Extract clean ID
        raw_id_data = item.get("post_id")
        if isinstance(raw_id_data, dict):
            clean_id = raw_id_data.get("activity_urn") or \
                      raw_id_data.get("ugcPost_urn") or \
                      f"post_{index}"
        else:
            clean_id = raw_id_data or f"post_{index}"
        
        # Extract posted date
        posted_info = item.get("posted_at", {})
        date_str = ""
        if isinstance(posted_info, dict):
            date_str = posted_info.get("date") or \
                      posted_info.get("relative") or ""
        else:
            date_str = posted_info or ""
        
        # Extract likes
        stats = item.get("stats", {})
        likes_count = 0
        if isinstance(stats, dict):
            likes_count = stats.get("likes") or \
                         stats.get("total_reactions") or 0
        else:
            likes_count = item.get("likes") or item.get("numLikes") or 0
        
        # Extract author
        author_info = item.get("author", {})
        author_name = ""
        if isinstance(author_info, dict):
            author_name = author_info.get("name") or \
                         f"{author_info.get('firstName', '')} " \
                         f"{author_info.get('lastName', '')}".strip()
        
        if not author_name:
            author_name = "Lenny Rachitsky"
        
        record = {
            "source": "linkedin",
            "post_id": clean_id,
            "url": item.get("url", ""),
            "text": item.get("text", ""),
            "posted_at": date_str,
            "likes": likes_count,
            "author": author_name
        }
        
        processed_items.append(record)
    
    return processed_items

