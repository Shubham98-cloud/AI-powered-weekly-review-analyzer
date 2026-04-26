import spacy
import re
from typing import List
from ingestion.models import Review

# Load spaCy model (English)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # Fallback if not downloaded
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Regex for phone numbers and emails
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b'

def scrub_text(text: str) -> str:
    """
    Remove PII (Names, Emails, Phone Numbers) from text.
    """
    if not text:
        return text
        
    # 1. Regex scrubbing (Emails/Phones)
    text = re.sub(EMAIL_REGEX, "[REDACTED_EMAIL]", text)
    text = re.sub(PHONE_REGEX, "[REDACTED_PHONE]", text)
    
    # 2. spaCy scrubbing (Names)
    doc = nlp(text)
    scrubbed_text = text
    # We iterate backwards to maintain indices
    entities = sorted(doc.ents, key=lambda x: x.start_char, reverse=True)
    for ent in entities:
        if ent.label_ in ["PERSON", "ORG"]:
            scrubbed_text = scrubbed_text[:ent.start_char] + f"[REDACTED_{ent.label_}]" + scrubbed_text[ent.end_char:]
            
    return scrubbed_text

def scrub_reviews(reviews: List[Review]) -> List[Review]:
    """
    Batch scrub a list of reviews.
    """
    print(f"Scrubbing PII from {len(reviews)} reviews...")
    for r in reviews:
        original_body = r.body
        r.body = scrub_text(r.body)
        r.title = scrub_text(r.title)
        
        if r.body != original_body:
            r.pii_redacted = True
            
    return reviews
