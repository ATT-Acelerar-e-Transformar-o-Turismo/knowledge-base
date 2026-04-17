from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import logging

from app.database import get_collection
from app.models.author import Author, AuthorCreate, AuthorUpdate
from app.utils import slugify

logger = logging.getLogger(__name__)

COLLECTION_NAME = "authors"


class AuthorService:
    def __init__(self) -> None:
        self._collection_name = COLLECTION_NAME

    @property
    def collection(self):
        return get_collection(self._collection_name)

    async def get_all(self) -> List[Author]:
        cursor = self.collection.find().sort("name", 1)
        authors = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            if not doc.get("slug"):
                doc["slug"] = slugify(doc["name"])
            authors.append(Author(**doc))
        return authors

    async def get_by_id(self, author_id: str) -> Optional[Author]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(author_id)})
        except InvalidId:
            return None
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        if not doc.get("slug"):
            doc["slug"] = slugify(doc["name"])
        return Author(**doc)

    async def get_by_slug(self, slug: str) -> Optional[Author]:
        doc = await self.collection.find_one({"slug": slug})
        if not doc:
            # Fallback: compute slug from name for authors that predate the slug field
            async for d in self.collection.find():
                if slugify(d.get("name", "")) == slug:
                    doc = d
                    break
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        if not doc.get("slug"):
            doc["slug"] = slugify(doc["name"])
        return Author(**doc)

    async def name_exists(self, name: str, exclude_id: str = None) -> bool:
        query = {"name": {"$regex": f"^{name}$", "$options": "i"}}
        if exclude_id:
            try:
                query["_id"] = {"$ne": ObjectId(exclude_id)}
            except InvalidId:
                pass
        return await self.collection.count_documents(query) > 0

    async def create(self, data: AuthorCreate) -> Author:
        if await self.name_exists(data.name):
            raise ValueError(f"Author with name '{data.name}' already exists")
        author_dict = data.model_dump()
        author_dict["slug"] = slugify(data.name)
        author_dict["created_at"] = datetime.now(timezone.utc)
        result = await self.collection.insert_one(author_dict)
        author_dict["_id"] = str(result.inserted_id)
        return Author(**author_dict)

    async def update(self, author_id: str, data: AuthorUpdate) -> Optional[Author]:
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_dict:
            return await self.get_by_id(author_id)
        # Capture old name before update for syncing posts matched by name
        old_name = None
        if "name" in update_dict:
            if await self.name_exists(update_dict["name"], exclude_id=author_id):
                raise ValueError(f"Author with name '{update_dict['name']}' already exists")
            update_dict["slug"] = slugify(update_dict["name"])
            old_author = await self.get_by_id(author_id)
            if old_author:
                old_name = old_author.name
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(author_id)},
                {"$set": update_dict}
            )
        except InvalidId:
            return None
        if result.matched_count == 0:
            return None
        # Sync denormalized fields to blog posts
        sync_fields = {k: v for k, v in update_dict.items() if k in ("name", "role")}
        if sync_fields:
            await self._sync_posts(author_id, sync_fields, old_name=old_name)
        return await self.get_by_id(author_id)

    async def _sync_posts(self, author_id: str, updates: dict, old_name: str = None) -> None:
        """Propagate author field changes to all blog posts matching this author."""
        posts_col = get_collection("blog_posts")
        post_fields = {}
        if "photo_url" in updates:
            post_fields["author_photo"] = updates["photo_url"]
        if "name" in updates:
            post_fields["author"] = updates["name"]
        if "role" in updates:
            post_fields["author_role"] = updates["role"]
        if not post_fields:
            return
        # Match by author_id OR by author name (for posts created before author_id was tracked)
        match_filter = {"$or": [{"author_id": author_id}]}
        if old_name:
            match_filter["$or"].append({"author": old_name})
        else:
            # Fetch current author name to match legacy posts
            author = await self.get_by_id(author_id)
            if author:
                match_filter["$or"].append({"author": author.name})
        # Also set author_id on matched posts so future syncs work by id
        post_fields["author_id"] = author_id
        await posts_col.update_many(match_filter, {"$set": post_fields})

    async def set_photo(self, author_id: str, photo_url: str) -> bool:
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(author_id)},
                {"$set": {"photo_url": photo_url}}
            )
        except InvalidId:
            return False
        if result.matched_count > 0:
            await self._sync_posts(author_id, {"photo_url": photo_url})
        return result.matched_count > 0

    async def set_cover(self, author_id: str, cover_url: str) -> bool:
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(author_id)},
                {"$set": {"cover_url": cover_url}}
            )
        except InvalidId:
            return False
        return result.matched_count > 0

    async def delete(self, author_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(author_id)})
        except InvalidId:
            return False
        return result.deleted_count > 0


_author_service = None

def get_author_service() -> AuthorService:
    global _author_service
    if _author_service is None:
        _author_service = AuthorService()
    return _author_service
