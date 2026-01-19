from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import logging

from app.database import get_collection
from app.models.blog_post import BlogPost, BlogPostCreate, BlogPostUpdate
from app.exceptions import BlogPostNotFoundError

logger = logging.getLogger(__name__)


COLLECTION_NAME = "blog_posts"


class BlogService:
    def __init__(self) -> None:
        self._collection_name = COLLECTION_NAME

    @property
    def collection(self):
        return get_collection(self._collection_name)

    async def create_post(self, post_data: BlogPostCreate) -> BlogPost:
        """Create a new blog post with auto-generated metadata."""
        post_dict = post_data.model_dump()
        current_time = datetime.now(timezone.utc)
        post_dict["created_at"] = current_time
        post_dict["updated_at"] = current_time
        post_dict["view_count"] = 0
        post_dict["attachments"] = []

        result = await self.collection.insert_one(post_dict)
        post_dict["_id"] = str(result.inserted_id)
        return BlogPost(**post_dict)

    async def get_post_by_id(self, post_id: str) -> Optional[BlogPost]:
        """Retrieve a blog post by its unique identifier."""
        try:
            post = await self.collection.find_one({"_id": ObjectId(post_id)})
            if post:
                post["_id"] = str(post["_id"])
                return BlogPost(**post)
        except InvalidId as e:
            logger.warning(f"Invalid ObjectId format for post_id={post_id}: {e}")
            return None
        return None

    async def get_published_posts(self, skip: int = 0, limit: int = 10) -> List[BlogPost]:
        """Get published blog posts with pagination"""
        cursor = self.collection.find(
            {"status": "published"},
            sort=[("published_at", -1)]
        ).skip(skip).limit(limit)

        posts = []
        async for post in cursor:
            post["_id"] = str(post["_id"])
            posts.append(BlogPost(**post))
        return posts

    async def get_all_posts(self, skip: int = 0, limit: int = 10) -> List[BlogPost]:
        """Get all blog posts (admin view) with pagination"""
        cursor = self.collection.find(
            {},
            sort=[("created_at", -1)]
        ).skip(skip).limit(limit)

        posts = []
        async for post in cursor:
            post["_id"] = str(post["_id"])
            posts.append(BlogPost(**post))
        return posts

    async def update_post(self, post_id: str, update_data: BlogPostUpdate) -> Optional[BlogPost]:
        """Update an existing blog post, setting published timestamp on status change."""
        try:
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            update_dict["updated_at"] = datetime.now(timezone.utc)

            if update_dict.get("status") == "published" and "published_at" not in update_dict:
                update_dict["published_at"] = datetime.now(timezone.utc)

            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": update_dict}
            )
            return await self.get_post_by_id(post_id)
        except InvalidId as e:
            logger.error(f"Invalid ObjectId format for post_id={post_id}: {e}")
            return None

    async def delete_post(self, post_id: str) -> bool:
        """Delete a blog post"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(post_id)})
            return result.deleted_count > 0
        except InvalidId as e:
            logger.error(f"Invalid ObjectId format for post_id={post_id}: {e}")
            return False

    async def increment_view_count(self, post_id: str):
        """Increment view count for a post"""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$inc": {"view_count": 1}}
            )
        except InvalidId as e:
            logger.warning(f"Failed to increment view count for invalid post_id={post_id}: {e}")

    async def add_attachment(self, post_id: str, attachment_data: dict) -> bool:
        """Add file attachment metadata to a blog post."""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$push": {"attachments": attachment_data}}
            )
            return True
        except InvalidId as e:
            logger.error(f"Failed to add attachment to invalid post_id={post_id}: {e}")
            return False

    async def remove_attachment(self, post_id: str, filename: str) -> bool:
        """Remove file attachment metadata from a blog post."""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$pull": {"attachments": {"filename": filename}}}
            )
            return True
        except InvalidId as e:
            logger.error(f"Failed to remove attachment from invalid post_id={post_id}: {e}")
            return False

    async def set_thumbnail(self, post_id: str, thumbnail_url: str) -> bool:
        """Set or update the thumbnail image URL for a blog post."""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": {"thumbnail_url": thumbnail_url}}
            )
            return True
        except InvalidId as e:
            logger.error(f"Failed to set thumbnail for invalid post_id={post_id}: {e}")
            return False

def get_blog_service() -> BlogService:
    """Dependency injection factory for BlogService."""
    return BlogService()