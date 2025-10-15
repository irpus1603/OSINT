#!/usr/bin/env python3
"""
Twitter scraper using official Twitter API v2 (requires API keys)
Alternative to snscrape when facing SSL/scraping issues.
"""

import argparse
import csv
import json
import os
import sys
from typing import List, Dict, Any, Optional
import tweepy
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def setup_api(bearer_token: str) -> tweepy.Client:
    """Initialize Twitter API client"""
    try:
        client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
        return client
    except Exception as e:
        sys.stderr.write(f"Error setting up Twitter API: {e}\n")
        sys.exit(1)

def search_tweets(client: tweepy.Client, query: str, max_results: int = 100,
                 since: Optional[str] = None, until: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search for tweets using Twitter API v2"""
    
    # Convert date strings to datetime objects if provided
    start_time = None
    end_time = None
    
    if since:
        start_time = datetime.fromisoformat(since)
    if until:
        end_time = datetime.fromisoformat(until)
    
    # Default to last 7 days if no dates provided (API limitation)
    if not start_time and not end_time:
        start_time = datetime.now(timezone.utc) - timedelta(days=6)  # 6 days to stay within limits
    
    try:
        print(f"Searching from {start_time} to {end_time if end_time else 'now'}")
        
        # First test the API connection
        try:
            me = client.get_me()
            print(f"Connected to Twitter API successfully")
        except Exception as e:
            print(f"API connection test failed: {e}")
            return []
        
        tweets_response = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang', 'geo'],
            user_fields=['username', 'name', 'verified'],
            expansions=['author_id'],
            start_time=start_time,
            end_time=end_time
        )
        
        if not tweets_response.data:
            print("No tweets found for the query.")
            return []
            
        results = []
        users = {}
        
        # Get user data from includes
        if tweets_response.includes and 'users' in tweets_response.includes:
            for user in tweets_response.includes['users']:
                users[user.id] = user
        
        # Process tweets
        for tweet in tweets_response.data:
            user = users.get(tweet.author_id, {})
            
            result = {
                'id': tweet.id,
                'url': f"https://twitter.com/i/web/status/{tweet.id}",
                'date': tweet.created_at.isoformat() if tweet.created_at else None,
                'content': tweet.text,
                'lang': tweet.lang,
                'username': getattr(user, 'username', None),
                'displayname': getattr(user, 'name', None),
                'user_verified': getattr(user, 'verified', None),
                'likeCount': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                'retweetCount': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                'replyCount': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                'quoteCount': tweet.public_metrics.get('quote_count', 0) if tweet.public_metrics else 0,
                'viewCount': None,  # Not available in API v2
                'sourceLabel': None,  # Not available in API v2
                'lon': None,  # Geo data processing needed
                'lat': None,
                'place_name': None,
                'place_type': None,
                'place_country': None,
                'place_countryCode': None,
            }
            
            # Process geo data if available
            if hasattr(tweet, 'geo') and tweet.geo:
                if 'coordinates' in tweet.geo:
                    coords = tweet.geo['coordinates']
                    if coords and len(coords) >= 2:
                        result['lon'] = coords[0]
                        result['lat'] = coords[1]
            
            results.append(result)
            
        return results
        
    except tweepy.TooManyRequests:
        sys.stderr.write("Rate limit exceeded. Please wait before making more requests.\n")
        return []
    except Exception as e:
        sys.stderr.write(f"Error searching tweets: {e}\n")
        return []

def write_jsonl(path: str, data: List[Dict[str, Any]]) -> int:
    """Write data to JSONL file"""
    with open(path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    return len(data)

def write_csv(path: str, data: List[Dict[str, Any]]) -> int:
    """Write data to CSV file"""
    if not data:
        return 0
    
    fieldnames = list(data[0].keys())
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    return len(data)

def main():
    parser = argparse.ArgumentParser(description="Twitter scraper using official API v2")
    parser.add_argument("-q", "--query", required=True, help="Search query")
    parser.add_argument("--bearer-token", help="Twitter API Bearer Token (or set TWITTER_BEARER_TOKEN env var)")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum tweets to fetch")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", help="End date (YYYY-MM-DD)")
    parser.add_argument("--out-prefix", default="tweets_api", help="Output file prefix")
    
    args = parser.parse_args()
    
    # Get bearer token
    bearer_token = args.bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
    if not bearer_token:
        sys.stderr.write(
            "Twitter API Bearer Token required. Set via --bearer-token or TWITTER_BEARER_TOKEN env var.\n"
            "Get your token from: https://developer.twitter.com/en/portal/dashboard\n"
        )
        sys.exit(1)
    
    # Setup API
    client = setup_api(bearer_token)
    
    print(f"Searching for: {args.query}")
    print(f"Max results: {args.max_results}")
    
    # Search tweets
    tweets = search_tweets(
        client, 
        args.query, 
        args.max_results,
        args.since,
        args.until
    )
    
    if not tweets:
        print("No tweets found or error occurred.")
        sys.exit(1)
    
    # Write outputs
    jsonl_path = f"{args.out_prefix}.jsonl"
    csv_path = f"{args.out_prefix}.csv"
    
    jsonl_count = write_jsonl(jsonl_path, tweets)
    csv_count = write_csv(csv_path, tweets)
    
    print(f"\nResults:")
    print(f"Found: {len(tweets)} tweets")
    print(f"Wrote: {jsonl_count} to {jsonl_path}")
    print(f"Wrote: {csv_count} to {csv_path}")

if __name__ == "__main__":
    main()