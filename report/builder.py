from typing import List
from datetime import datetime
from .models import ReportPayload, Theme
from ingestion.models import Review

def build_report_payload(
    product: str,
    iso_week: str,
    reviews: List[Review],
    themes: List[Theme]
) -> ReportPayload:
    """
    Assembles raw review data and NLP themes into a single report payload.
    """
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0.0
    
    return ReportPayload(
        product=product,
        iso_week=iso_week,
        run_at=datetime.utcnow(),
        reviews_analysed=len(reviews),
        clusters_found=len(themes),
        avg_rating=avg_rating,
        themes=themes
    )
