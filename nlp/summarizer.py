import os
import json
from groq import Groq
from typing import List, Dict
from report.models import Theme

SUMMARIZER_PROMPT = """
You are a product analyst. Analyze the following group of app reviews and identify the single most prominent THEME.
Return your response in strict JSON format.

Constraints:
- theme_name: Max 6 words.
- quotes: Select 2-3 verbatim quotes that best represent the theme.
- action_ideas: 1-2 actionable product or engineering ideas, max 25 words each.

Reviews:
{reviews_text}
"""

def summarize_cluster(reviews_text: str, model: str = "llama-3.1-70b-versatile") -> Theme:
    """
    Summarize a cluster of reviews using Groq (Llama 3).
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY", "PLACEHOLDER_GROQ_KEY"))
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful analyst that outputs JSON."},
                {"role": "user", "content": SUMMARIZER_PROMPT.format(reviews_text=reviews_text)}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return Theme(
            theme_name=result.get("theme_name", "Unknown Theme"),
            review_count=0, 
            avg_rating=0.0, 
            quotes=result.get("quotes", []),
            action_ideas=result.get("action_ideas", [])
        )
    except Exception as e:
        print(f"Error summarizing cluster with Groq: {e}")
        return Theme(theme_name="Analysis Failed", review_count=0, avg_rating=0.0)

def generate_themes(clustered_reviews: Dict[int, List], model: str = "llama-3.1-70b-versatile") -> List[Theme]:
    """
    Generate themes for all clusters using Groq.
    """
    themes = []
    for label, reviews in clustered_reviews.items():
        if label == -1: continue # Skip noise
        
        print(f"Summarizing Theme {label} ({len(reviews)} reviews) using Groq...")
        # Sample reviews to stay within context limits
        sampled = reviews[:40]
        reviews_text = "\n---\n".join([f"Rating: {r.rating}\n{r.body}" for r in sampled])
        
        theme = summarize_cluster(reviews_text, model)
        theme.review_count = len(reviews)
        theme.avg_rating = sum(r.rating for r in reviews) / len(reviews)
        
        themes.append(theme)
        
    return themes
