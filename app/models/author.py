from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.utils import slugify  # noqa: F401 — re-exported for backwards compatibility


class Author(BaseModel):
    id: Optional[str] = Field(None, validation_alias="_id")
    name: str
    slug: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None  # e.g. "Doutoramento em Turismo"
    photo_url: Optional[str] = None
    cover_url: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    github: Optional[str] = None
    orcid: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AuthorCreate(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    github: Optional[str] = None
    orcid: Optional[str] = None


class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    github: Optional[str] = None
    orcid: Optional[str] = None
