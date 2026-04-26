import emoji
from langdetect import detect, DetectorFactory
from datetime import datetime, timezone, timedelta
from typing import List
from ingestion.appstore import fetch_appstore_reviews
from ingestion.playstore import fetch_playstore_reviews
from ingestion.models import Review

# For consistent language detection
DetectorFactory.seed = 0

def has_emoji(text: str) -> bool:
    """Check if text contains any emoji."""
    return emoji.emoji_count(text) > 0

def is_english(text: str) -> bool:
    """Check if text is primarily English."""
    if not text.strip():
        return False
    try:
        return detect(text) == 'en'
    except:
        return False

def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())

def filter_review(review: Review) -> bool:
    """
    Apply user-requested filters:
    - No emojis
    - English only
    - At least 4 words
    """
    # 1. Emoji check
    if has_emoji(review.body) or has_emoji(review.title):
        return False
        
    # 2. Word count check (less than 4 words = remove)
    if count_words(review.body) < 4:
        return False
        
    # 3. Language check
    if not is_english(review.body):
        return False
        
    return True

def fetch_reviews(product_name: str, appstore_id: str, playstore_id: str, window_weeks: int) -> List[Review]:
    """
    Facade to fetch and filter reviews from both platforms.
    """
    print(f"Fetching reviews for {product_name}...")
    
    as_raw = fetch_appstore_reviews(appstore_id, window_weeks)
    ps_raw = fetch_playstore_reviews(playstore_id, window_weeks)
    
    raw_combined = as_raw + ps_raw
    for r in raw_combined:
        r.product = product_name
        
    # Apply time window filter
    cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=window_weeks)
    in_window = [r for r in raw_combined if r.date >= cutoff_date]
    
    # Apply user filters
    filtered = [r for r in in_window if filter_review(r)]
    
    print(f"Total raw: {len(raw_combined)}, In window: {len(in_window)}, After filtering: {len(filtered)}")
    return filtered
