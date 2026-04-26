import spacy
from typing import List
from ingestion.models import Review

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def is_substantive(text: str) -> bool:
    """
    Heuristic to check if a review has substance.
    Must have at least one Noun and one Verb/Adjective.
    """
    if not text or len(text.split()) < 4:
        return False
        
    doc = nlp(text)
    
    has_noun = any(token.pos_ in ["NOUN", "PROPN"] for token in doc)
    has_action_or_desc = any(token.pos_ in ["VERB", "ADJ"] for token in doc)
    
    # Word diversity check (unique words / total words)
    words = [t.text.lower() for t in doc if not t.is_punct]
    if not words: return False
    diversity = len(set(words)) / len(words)
    
    return has_noun and has_action_or_desc and (diversity > 0.5)

def filter_by_heuristics(reviews: List[Review]) -> List[Review]:
    """
    Filter out reviews that lack semantic substance.
    """
    print(f"Applying Heuristic Filter to {len(reviews)} reviews...")
    filtered = [r for r in reviews if is_substantive(r.body)]
    print(f"Heuristic Filter: {len(reviews)} -> {len(filtered)} (Removed {len(reviews) - len(filtered)} low-substance reviews)")
    return filtered
