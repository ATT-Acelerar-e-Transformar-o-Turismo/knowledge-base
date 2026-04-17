from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BlogPost(BaseModel):
    id: Optional[str] = Field(None, validation_alias="_id")
    title: str
    title_en: Optional[str] = None
    content: str  # Rich text content
    content_en: Optional[str] = None
    excerpt: Optional[str] = None  # Short description/summary
    excerpt_en: Optional[str] = None
    thumbnail_url: Optional[str] = None
    author: str
    author_id: Optional[str] = None
    author_photo: Optional[str] = None  # URL to author profile photo
    author_role: Optional[str] = None  # e.g. "Doutoramento em Turismo"
    post_type: str = "news-event"  # "news-event" or "publication"
    publication_link: Optional[str] = None  # External URL to the publication
    publication_link_label: Optional[str] = None  # Display label for the link
    publication_link_label_en: Optional[str] = None
    status: str = "draft"  # draft, published
    categories: List[str] = []  # category slugs
    keywords: List[str] = []  # free-form keywords
    tags: List[str] = []  # deprecated, kept for backward compatibility
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
    title_en: Optional[str] = None
    content: str
    content_en: Optional[str] = None
    excerpt: Optional[str] = None
    excerpt_en: Optional[str] = None
    author: str
    author_id: Optional[str] = None
    author_photo: Optional[str] = None
    author_role: Optional[str] = None
    post_type: str = "news-event"
    publication_link: Optional[str] = None
    publication_link_label: Optional[str] = None
    publication_link_label_en: Optional[str] = None
    status: str = "draft"
    categories: List[str] = []
    keywords: List[str] = []
    tags: List[str] = []


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    title_en: Optional[str] = None
    content: Optional[str] = None
    content_en: Optional[str] = None
    excerpt: Optional[str] = None
    excerpt_en: Optional[str] = None
    author: Optional[str] = None
    author_id: Optional[str] = None
    author_photo: Optional[str] = None
    author_role: Optional[str] = None
    post_type: Optional[str] = None
    publication_link: Optional[str] = None
    publication_link_label: Optional[str] = None
    publication_link_label_en: Optional[str] = None
    status: Optional[str] = None
    categories: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    published_at: Optional[datetime] = None


class FileAttachment(BaseModel):
    filename: str
    original_filename: str
    url: str
    size: int
    mime_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)