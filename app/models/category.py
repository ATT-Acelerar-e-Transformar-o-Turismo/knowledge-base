from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Category(BaseModel):
    id: Optional[str] = Field(None, validation_alias="_id")
    name_pt: str
    name_en: str
    slug: Optional[str] = None
    type: str  # "news-event" or "publication"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CategoryCreate(BaseModel):
    name_pt: str
    name_en: str
    type: str  # "news-event" or "publication"


class CategoryUpdate(BaseModel):
    name_pt: Optional[str] = None
    name_en: Optional[str] = None
    type: Optional[str] = None
