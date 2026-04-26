from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional

class Review(BaseModel):
    review_id: str
    product: str
    platform: Literal["appstore", "playstore"]
    author: str
    rating: int = Field(..., ge=1, le=5)
    title: str = ""
    body: str
    date: datetime
    version: Optional[str] = None
    pii_redacted: bool = False

    class Config:
        orm_mode = True
