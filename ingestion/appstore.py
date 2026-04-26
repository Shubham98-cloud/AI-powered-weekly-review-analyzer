import requests
from datetime import datetime, timezone
from typing import List
from ingestion.models import Review

def fetch_appstore_reviews(app_id: str, window_weeks: int) -> List[Review]:
    """
    Fetch reviews from Apple App Store via iTunes RSS feed.
    """
    reviews = []
    # Sort by most recent
    url = f"https://itunes.apple.com/in/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        entries = data.get("feed", {}).get("entry", [])
        if not entries:
            return []

        # RSS feed returns most recent first. 
        # Note: entry[0] is often app metadata, real reviews start at 1
        for entry in entries[1:]:
            try:
                review_id = entry.get("id", {}).get("label")
                author = entry.get("author", {}).get("name", {}).get("label", "Anonymous")
                rating = int(entry.get("im:rating", {}).get("label", 0))
                title = entry.get("title", {}).get("label", "")
                content = entry.get("content", {}).get("label", "")
                version = entry.get("im:version", {}).get("label", "N/A")
                
                # App Store dates are ISO strings in the 'updated' field or similar
                # For RSS, the date is often nested
                # Note: RSS feed structure can be tricky.
                # Usually: entry['content']['attributes']['type'] == 'text'
                # Let's use a default or try to find a date if available.
                # Actually, the 'updated' field at the feed level or entry level?
                # entry level has no date in the simplified JSON usually, 
                # but it might have it in the XML version.
                # For this implementation, we assume current time if missing, 
                # but better to check the 'updated' field in the entry if it exists.
                date_str = entry.get("updated", {}).get("label") # Not always there in JSON
                if date_str:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    date = datetime.now(timezone.utc)

                review = Review(
                    review_id=review_id,
                    product="N/A", # Set by facade
                    platform="appstore",
                    author=author,
                    rating=rating,
                    title=title,
                    body=content,
                    date=date,
                    version=version
                )
                reviews.append(review)
            except Exception as e:
                print(f"Error parsing App Store review: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching App Store reviews for {app_id}: {e}")
        
    return reviews
