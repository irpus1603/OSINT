import feedparser
import requests
import time
import hashlib
from datetime import datetime
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from django.utils import timezone
from celery import shared_task
from .models import Source, Keyword, Article, Post
import tweepy
import os
from django.conf import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure we have a console handler for immediate output
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Compile keyword patterns for matching
import re

# English keyword patterns
EN_KEYWORD_PATTERNS = [
    r"\bterror(ism|ist|ize|ized|izing|s)?\b",
    r"\bbomb(ing|ings|ed|s)?\b",
    r"\bexplos(ion|ive|ives|ions)\b",
    r"\battack(s|ed|ing)?\b",
    r"\bmilitant(s)?\b",
    r"\binsurg(en(t|cy)|ents?)\b",
    r"\bhostage(s|taking)?\b",
    r"\bshoot(ing|ings|er|ers)?\b",
    r"\bthreat(s|ened|ening)?\b",
    r"\bsecurity\b",
    r"\briot(s|ing)?\b",
    r"\bprotest(s|er|ers|ing)?\b",
    r"\bdemonstrat(e|ion|ions|or|ors|ing|ed|es)\b",
    r"\bextrem(ist|ism|ists)?\b",
    r"\bradicali(s|z)(e|ed|ing|ation)\b",
    r"\bcyber(-|\s)?attack(s|ed|ing)?\b",
]

# Indonesian keyword patterns
ID_KEYWORD_PATTERNS = [
    r"\bteror(isme|is|isnya)?\b",
    r"\bbom(ber|bunuhdiri| meledak| meledakkan| ledakan)?\b",
    r"\bledak(an|an\-)?\b",
    r"\bserang(an| menyerang| diserang)?\b",
    r"\bkerusuh(an)?\b",
    r"\bdemo(nstrasi)?\b",
    r"\bunjuk\s?rasa\b",
    r"\bpenculikan\b",
    r"\bsandera\b",
    r"\bancam(an| mengancam)?\b",
    r"\bkeamanan\b",
    r"\bekstrem(is|isme)?\b",
    r"\bradikalisasi\b",
    r"\bpenembak(an)?\b",
]

# Compile all regex patterns
ALL_KEYWORD_REGEXES = [re.compile(p, flags=re.IGNORECASE) for p in EN_KEYWORD_PATTERNS + ID_KEYWORD_PATTERNS]

def match_keywords(text):
    """Return set of keyword patterns that matched."""
    hits = set()
    if not text:
        return hits
    for rx in ALL_KEYWORD_REGEXES:
        if rx.search(text):
            hits.add(rx.pattern)
    return hits

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "ignore")).hexdigest()

def parse_pubdate(entry) -> datetime:
    """Parse RSS pubDate/updated fields, fallback to now (UTC)"""
    for key in ("published", "updated", "pubDate"):
        if key in entry and entry[key]:
            try:
                dt = parsedate_to_datetime(entry[key])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                pass
    return timezone.now()

def extract_text_from_html(html: str) -> str:
    """Extract text content from HTML"""
    soup = BeautifulSoup(html, "lxml")
    # Remove script/style
    for s in soup(["script", "style", "noscript"]):
        s.extract()
    # Prefer article content if present
    candidates = []
    for selector in ["article", "main", "div#content", "div.article", "div.post", "section.article"]:
        for node in soup.select(selector):
            candidates.append(node.get_text(separator=" ", strip=True))
    # Fallback to all paragraphs
    if not candidates:
        paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]
        candidates.append(" ".join(paragraphs))
    # Return the longest chunk as the main text
    candidates = [c for c in candidates if c]
    if not candidates:
        return ""
    return max(candidates, key=len)

def fetch_full_article(url: str) -> str:
    """Fetch and extract full article text"""
    try:
        headers = {
            "User-Agent": "SecurityNewsCrawler/1.0 (+https://example.org/)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200 or not r.text:
            return ""
        return extract_text_from_html(r.text)
    except Exception:
        return ""

@shared_task
def scrape_news_source(source_id):
    """Scrape a news source using RSS feeds"""
    try:
        source = Source.objects.get(id=source_id, source_type='news', is_active=True)
        logger.info(f"Starting scrape_news_source for {source.name} (ID: {source_id})")
    except Source.DoesNotExist:
        error_msg = f"Source with ID {source_id} not found or inactive"
        logger.error(error_msg)
        return error_msg
    
    # Get active keywords
    keywords = Keyword.objects.filter(is_active=True)
    keyword_terms = [kw.term for kw in keywords]
    logger.info(f"Found {keywords.count()} active keywords for matching")
    
    try:
        # Parse RSS feed
        logger.info(f"Parsing RSS feed: {source.url}")
        parsed = feedparser.parse(source.url)
        logger.info(f"Feed parsed. Bozo flag: {parsed.bozo}. Entries found: {len(parsed.entries)}")
        
        if parsed.bozo:
            logger.warning(f"Feed parsing warnings for {source.name}: {getattr(parsed, 'bozo_exception', 'Unknown warning')}")
        
        articles_created = 0
        articles_skipped = 0
        
        for i, entry in enumerate(parsed.entries):
            url = entry.get("link") or ""
            title = (entry.get("title") or "").strip()
            summary = (entry.get("summary") or entry.get("description") or "").strip()
            published_at = parse_pubdate(entry)
            
            if not url:
                logger.debug(f"Skipping entry {i+1}: No URL found")
                articles_skipped += 1
                continue
            
            # Check if article already exists
            if Article.objects.filter(url=url).exists():
                logger.debug(f"Skipping entry {i+1}: Article already exists ({url})")
                articles_skipped += 1
                continue
            
            # Create base text for keyword matching
            base_text = f"{title}\n{summary}"
            hits = match_keywords(base_text)
            
            # If no matches in title/summary, try full article
            full_text = ""
            if not hits:
                logger.debug(f"Entry {i+1}: No keyword matches in title/summary, fetching full article")
                time.sleep(0.7)  # Rate limiting
                full_text = fetch_full_article(url)
                if full_text:
                    hits = match_keywords(f"{base_text}\n{full_text}")
            
            # If we have keyword matches, save the article
            if hits:
                logger.info(f"Entry {i+1}: Keyword matches found - {hits}")
                excerpt = (summary or full_text[:500]).replace("\n", " ").strip()
                
                # Create article
                try:
                    article = Article.objects.create(
                        title=title,
                        url=url,
                        content=full_text or summary,
                        excerpt=excerpt,
                        published_at=published_at,
                        source=source
                    )
                    
                    # Match keywords and add to article
                    matched_keywords = []
                    for keyword in keywords:
                        if keyword.term.lower() in (full_text + " " + title + " " + summary).lower():
                            matched_keywords.append(keyword)
                    
                    article.keywords.set(matched_keywords)
                    articles_created += 1
                    logger.info(f"Created article: {title[:50]}...")
                except Exception as e:
                    logger.error(f"Error creating article '{title}': {str(e)}")
                    articles_skipped += 1
            else:
                logger.debug(f"Entry {i+1}: No keyword matches found")
                articles_skipped += 1
        
        result_msg = f"Successfully scraped {source.name}. Created {articles_created} articles, skipped {articles_skipped}."
        logger.info(result_msg)
        return result_msg
        
    except Exception as e:
        error_msg = f"Error scraping {source.name}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@shared_task
def scrape_social_media_source(source_id):
    """Scrape social media source (Twitter)"""
    try:
        source = Source.objects.get(id=source_id, source_type='social', is_active=True)
        logger.info(f"Starting scrape_social_media_source for {source.name} (ID: {source_id})")
    except Source.DoesNotExist:
        error_msg = f"Source with ID {source_id} not found or inactive"
        logger.error(error_msg)
        return error_msg
    
    # Check if Twitter Bearer Token is available
    bearer_token = getattr(settings, 'TWITTER_BEARER_TOKEN', None)
    if not bearer_token:
        error_msg = "Twitter Bearer Token not configured in settings"
        logger.error(error_msg)
        return error_msg
    
    # Get active keywords
    keywords = Keyword.objects.filter(is_active=True)
    keyword_terms = [kw.term for kw in keywords]
    logger.info(f"Found {keywords.count()} active keywords for Twitter search")
    
    # Create search query from keywords
    query = " OR ".join([f'"{term}"' for term in keyword_terms[:10]])  # Limit to 10 terms
    logger.info(f"Twitter search query: {query}")
    
    try:
        # Initialize Twitter API client
        client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
        logger.info("Initialized Twitter API client")
        
        # Search for tweets
        tweets_response = client.search_recent_tweets(
            query=query,
            max_results=50,  # Limit to 50 for testing
            tweet_fields=['created_at', 'author_id', 'public_metrics'],
            user_fields=['username', 'name'],
            expansions=['author_id']
        )
        logger.info(f"Twitter search completed. Response data: {bool(tweets_response.data) if tweets_response else False}")
        
        if not tweets_response.data:
            result_msg = f"No tweets found for keywords from {source.name}"
            logger.info(result_msg)
            return result_msg
        
        # Process user data
        users = {}
        if tweets_response.includes and 'users' in tweets_response.includes:
            for user in tweets_response.includes['users']:
                users[user.id] = user
        logger.info(f"Processed {len(users)} user profiles from Twitter response")
        
        posts_created = 0
        for tweet in tweets_response.data:
            # Check if post already exists
            url = f"https://twitter.com/i/web/status/{tweet.id}"
            if Post.objects.filter(url=url).exists():
                logger.debug(f"Skipping tweet {tweet.id}: Already exists in database")
                continue
            
            # Get user information
            user = users.get(tweet.author_id, {})
            
            # Create post
            try:
                post = Post.objects.create(
                    content=tweet.text,
                    url=url,
                    author=getattr(user, 'name', ''),
                    author_username=getattr(user, 'username', ''),
                    published_at=tweet.created_at,
                    source=source,
                    likes_count=tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                    retweets_count=tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                    replies_count=tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0
                )
                
                # Match keywords and add to post
                matched_keywords = []
                for keyword in keywords:
                    if keyword.term.lower() in tweet.text.lower():
                        matched_keywords.append(keyword)
                
                post.keywords.set(matched_keywords)
                posts_created += 1
                logger.info(f"Created Twitter post: {tweet.text[:50]}...")
            except Exception as e:
                logger.error(f"Error creating Twitter post: {str(e)}")
        
        result_msg = f"Successfully scraped {source.name}. Created {posts_created} posts."
        logger.info(result_msg)
        return result_msg
        
    except Exception as e:
        error_msg = f"Error scraping {source.name}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@shared_task
def run_scheduled_scraping():
    """Run scheduled scraping for all active sources"""
    logger.info("Starting run_scheduled_scraping for all active sources")
    active_sources = Source.objects.filter(is_active=True)
    logger.info(f"Found {active_sources.count()} active sources")
    
    results = []
    for source in active_sources:
        logger.info(f"Processing source: {source.name} (Type: {source.source_type})")
        if source.source_type == 'news':
            result = scrape_news_source.delay(source.id)
            results.append(f"News scraping queued for {source.name}: {result.id}")
            logger.info(f"Queued news scraping for {source.name}")
        elif source.source_type == 'social':
            result = scrape_social_media_source.delay(source.id)
            results.append(f"Social media scraping queued for {source.name}: {result.id}")
            logger.info(f"Queued social media scraping for {source.name}")
    
    result_msg = f"Scheduled scraping started for {len(results)} sources:\n" + "\n".join(results)
    logger.info(result_msg)
    return result_msg