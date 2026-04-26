from thefuzz import fuzz
from typing import List
from report.models import Theme
from ingestion.models import Review

def validate_quotes(themes: List[Theme], reviews: List[Review], threshold: int = 85) -> List[Theme]:
    """
    Ensure every quote in the themes actually exists in the raw reviews.
    Rejects quotes that fail the fuzzy match threshold.
    """
    print(f"Validating quotes for {len(themes)} themes...")
    
    # Pre-calculate review bodies for faster lookup
    all_bodies = [r.body for r in reviews]
    
    for theme in themes:
        validated_quotes = []
        for quote in theme.quotes:
            # Find best match in all reviews
            # Note: For performance, we could search only within the cluster's reviews
            best_ratio = 0
            for body in all_bodies:
                ratio = fuzz.partial_ratio(quote.lower(), body.lower())
                if ratio > best_ratio:
                    best_ratio = ratio
                if best_ratio >= threshold:
                    break
            
            if best_ratio >= threshold:
                validated_quotes.append(quote)
            else:
                print(f"Warning: Dropped hallucinated quote (ratio {best_ratio}): {quote[:50]}...")
                
        theme.quotes = validated_quotes
        
    return themes
