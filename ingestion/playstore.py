from google_play_scraper import reviews, Sort
from datetime import datetime, timezone, timedelta
from typing import List
from ingestion.models import Review

def fetch_playstore_reviews(package_id: str, window_weeks: int) -> List[Review]:
    """
    Fetch reviews from Google Play Store using google-play-scraper.
    """
    all_reviews = []
    
    try:
        # Fetching a batch of reviews
        # Note: In a production app, we'd loop with continuation_token
        # For the skeleton, we fetch the first 200 reviews
        result, continuation_token = reviews(
            package_id,
            lang='en', # User asked to remove non-English, but scraper can filter early
            country='in',
            sort=Sort.NEWEST,
            count=200
        )
        
        for r in result:
            try:
                # Convert date to UTC
                date = r['at'].replace(tzinfo=timezone.utc)
                
                review = Review(
                    review_id=r['reviewId'],
                    product="N/A", # Set by facade
                    platform="playstore",
                    author=r['userName'],
                    rating=r['score'],
                    title="", # Play Store reviews don't have separate titles usually
                    body=r['content'],
                    date=date,
                    version=r.get('reviewCreatedVersion', 'N/A')
                )
                all_reviews.append(review)
            except Exception as e:
                print(f"Error parsing Play Store review: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching Play Store reviews for {package_id}: {e}")
        
    return all_reviews
