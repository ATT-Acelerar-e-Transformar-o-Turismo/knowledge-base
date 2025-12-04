from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.database import get_collection
from app.models.blog_post import BlogPost, BlogPostCreate, BlogPostUpdate


class BlogService:
    def __init__(self):
        self.collection_name = "blog_posts"

    @property
    def collection(self):
        return get_collection(self.collection_name)

    async def create_post(self, post_data: BlogPostCreate) -> BlogPost:
        """Create a new blog post"""
        post_dict = post_data.model_dump()
        post_dict["created_at"] = datetime.utcnow()
        post_dict["updated_at"] = datetime.utcnow()
        post_dict["view_count"] = 0
        post_dict["attachments"] = []

        result = await self.collection.insert_one(post_dict)
        post_dict["_id"] = str(result.inserted_id)
        return BlogPost(**post_dict)

    async def get_post_by_id(self, post_id: str) -> Optional[BlogPost]:
        """Get a blog post by ID"""
        try:
            post = await self.collection.find_one({"_id": ObjectId(post_id)})
            if post:
                post["_id"] = str(post["_id"])
                return BlogPost(**post)
        except Exception:
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
        """Update a blog post"""
        try:
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()

            # Set published_at when status changes to published
            if update_dict.get("status") == "published" and "published_at" not in update_dict:
                update_dict["published_at"] = datetime.utcnow()

            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": update_dict}
            )
            return await self.get_post_by_id(post_id)
        except Exception:
            return None

    async def delete_post(self, post_id: str) -> bool:
        """Delete a blog post"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(post_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def increment_view_count(self, post_id: str):
        """Increment view count for a post"""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$inc": {"view_count": 1}}
            )
        except Exception:
            pass

    async def add_attachment(self, post_id: str, attachment_data: dict):
        """Add file attachment to a blog post"""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$push": {"attachments": attachment_data}}
            )
            return True
        except Exception:
            return False

    async def remove_attachment(self, post_id: str, filename: str):
        """Remove file attachment from a blog post"""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$pull": {"attachments": {"filename": filename}}}
            )
            return True
        except Exception:
            return False

    async def set_thumbnail(self, post_id: str, thumbnail_url: str):
        """Set thumbnail image for a blog post"""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": {"thumbnail_url": thumbnail_url}}
            )
            return True
        except Exception:
            return False

def get_blog_service():
    return BlogService()

# Deprecated - do not use, kept for compatibility
# blog_service = BlogService()