import os
import google.generativeai as genai
from typing import List
from ingestion.models import Review

def get_embeddings(texts: List[str], model: str = "models/text-embedding-004") -> List[List[float]]:
    """
    Get embeddings for a list of texts using Google Gemini.
    """
    if not texts:
        return []
        
    api_key = os.getenv("GOOGLE_API_KEY", "PLACEHOLDER_GOOGLE_KEY")
    genai.configure(api_key=api_key)
    
    try:
        # Gemini allows batching up to 100 texts per request
        result = genai.embed_content(
            model=model,
            content=texts,
            task_type="clustering"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating Gemini embeddings: {e}")
        return []

def embed_reviews(reviews: List[Review], model: str = "models/text-embedding-004") -> List[List[float]]:
    """
    Generate embeddings for a list of reviews (Title + Body) using Gemini.
    """
    print(f"Generating Gemini embeddings for {len(reviews)} reviews...")
    # Combine title and body
    combined_texts = [f"{r.title}. {r.body}".strip() for r in reviews]
    # Truncate texts to stay within limits
    truncated_texts = [text[:2000] for text in combined_texts]
    
    # Process in batches of 100 (Gemini limit)
    all_embeddings = []
    for i in range(0, len(truncated_texts), 100):
        batch = truncated_texts[i:i+100]
        batch_embeddings = get_embeddings(batch, model=model)
        all_embeddings.extend(batch_embeddings)
        
    return all_embeddings
