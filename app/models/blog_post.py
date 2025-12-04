from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BlogPost(BaseModel):
    id: Optional[str] = Field(None, validation_alias="_id")
    title: str
    content: str  # Rich text content
    excerpt: Optional[str] = None  # Short description/summary
    thumbnail_url: Optional[str] = None
    author: str
    status: str = "draft"  # draft, published
    tags: List[str] = []
    attachments: List[dict] = []  # List of {"filename": str, "url": str, "size": int}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    view_count: int = 0

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BlogPostCreate(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    author: str
    status: str = "draft"
    tags: List[str] = []


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    published_at: Optional[datetime] = None


class FileAttachment(BaseModel):
    filename: str
    original_filename: str
    url: str
    size: int
    mime_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)