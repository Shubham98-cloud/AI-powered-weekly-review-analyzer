import re
from typing import List
from ingestion.models import Review

# Regex for phone numbers and emails
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b'

def scrub_text(text: str) -> str:
    """
    Remove PII (Emails, Phone Numbers) from text using Regex.
    Lightweight version for serverless/cloud environments.
    """
    if not text:
        return text
        
    text = re.sub(EMAIL_REGEX, "[REDACTED_EMAIL]", text)
    text = re.sub(PHONE_REGEX, "[REDACTED_PHONE]", text)
    return text

def scrub_reviews(reviews: List[Review]) -> List[Review]:
    """
    Batch scrub a list of reviews.
    """
    for r in reviews:
        original_body = r.body
        r.body = scrub_text(r.body)
        r.title = scrub_text(r.title)
        
        if r.body != original_body:
            r.pii_redacted = True
            
    return reviews
