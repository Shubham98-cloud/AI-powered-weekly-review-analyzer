import os
import google.generativeai as genai
import json
from typing import List, Dict
from ingestion.models import Review

def cluster_embeddings(reviews: List[Review], *args, **kwargs) -> List[int]:
    """
    Replaced local HDBSCAN with Gemini-based semantic grouping to save bundle size.
    Returns a list of 'labels' (0, 1, 2...) for each review.
    """
    if len(reviews) < 3:
        return [0] * len(reviews)

    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Prepare a list for Gemini to group
    review_data = [{"id": i, "text": f"{r.title}: {r.body}"[:200]} for i, r in enumerate(reviews)]
    
    prompt = f"""
    Group these app reviews into 3-5 distinct semantic clusters. 
    Return ONLY a JSON mapping of cluster_id (int) to a list of review_ids (int).
    Reviews: {json.dumps(review_data)}
    """

    try:
        response = model.generate_content(prompt)
        # Extract JSON from response
        raw_text = response.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        
        clusters = json.loads(raw_text)
        
        # Convert mapping back to label list
        labels = [-1] * len(reviews)
        for cluster_id, review_ids in clusters.items():
            for rid in review_ids:
                if rid < len(labels):
                    labels[rid] = int(cluster_id)
        return labels
    except Exception as e:
        print(f"Clustering fallback: {e}")
        return [0] * len(reviews)
