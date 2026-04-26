import re
from typing import List
from ingestion.models import Review

def is_substantive(text: str) -> bool:
    """
    Lightweight heuristic to check if a review has substance.
    Uses word count and diversity instead of heavy POS tagging.
    """
    if not text:
        return False
        
    words = text.split()
    if len(words) < 5:
        return False
        
    # Diversity check: ensure it's not just "good good good good"
    unique_words = set([w.lower() for w in words])
    diversity = len(unique_words) / len(words)
    
    return diversity > 0.6

def filter_by_heuristics(reviews: List[Review]) -> List[Review]:
    """
    Filter out reviews that lack semantic substance.
    """
    print(f"Applying Lightweight Heuristic Filter...")
    filtered = [r for r in reviews if is_substantive(r.body)]
    print(f"Filter Results: {len(reviews)} -> {len(filtered)}")
    return filtered
