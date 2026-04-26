from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class Theme(BaseModel):
    theme_name: str = Field(..., description="Name of the theme, max 6 words")
    review_count: int
    avg_rating: float
    quotes: List[str] = Field(default_factory=list, description="2-3 verbatim quotes")
    action_ideas: List[str] = Field(default_factory=list, description="1-2 actionable ideas")

class ReportPayload(BaseModel):
    product: str
    iso_week: str
    run_at: datetime = Field(default_factory=datetime.utcnow)
    reviews_analysed: int
    clusters_found: int
    avg_rating: float
    themes: List[Theme]
    doc_url: Optional[str] = None
    heading_anchor: Optional[str] = None
    gmail_message_id: Optional[str] = None
