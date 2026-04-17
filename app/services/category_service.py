from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import logging

from app.database import get_collection
from app.models.category import Category, CategoryCreate, CategoryUpdate
from app.utils import slugify

logger = logging.getLogger(__name__)

COLLECTION_NAME = "categories"


class CategoryService:
    def __init__(self) -> None:
        self._collection_name = COLLECTION_NAME

    @property
    def collection(self):
        return get_collection(self._collection_name)

    async def get_all(self) -> List[Category]:
        cursor = self.collection.find().sort([("type", 1), ("name_pt", 1)])
        categories = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            categories.append(Category(**doc))
        return categories

    async def get_by_type(self, type: str) -> List[Category]:
        cursor = self.collection.find({"type": type}).sort("name_pt", 1)
        categories = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            categories.append(Category(**doc))
        return categories

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        doc = await self.collection.find_one({"slug": slug})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return Category(**doc)

    async def get_by_id(self, category_id: str) -> Optional[Category]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(category_id)})
        except InvalidId:
            return None
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return Category(**doc)

    async def slug_exists(self, slug: str, exclude_id: str = None) -> bool:
        query = {"slug": slug}
        if exclude_id:
            try:
                query["_id"] = {"$ne": ObjectId(exclude_id)}
            except InvalidId:
                pass
        return await self.collection.count_documents(query) > 0

    async def create(self, data: CategoryCreate) -> Category:
        slug = slugify(data.name_pt)
        if await self.slug_exists(slug):
            raise ValueError(f"Category with slug '{slug}' already exists")
        cat_dict = data.model_dump()
        cat_dict["slug"] = slug
        cat_dict["created_at"] = datetime.now(timezone.utc)
        result = await self.collection.insert_one(cat_dict)
        cat_dict["_id"] = str(result.inserted_id)
        return Category(**cat_dict)

    async def update(self, category_id: str, data: CategoryUpdate) -> Optional[Category]:
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_dict:
            return await self.get_by_id(category_id)

        old_slug = None
        if "name_pt" in update_dict:
            old_cat = await self.get_by_id(category_id)
            if old_cat:
                old_slug = old_cat.slug
            new_slug = slugify(update_dict["name_pt"])
            if await self.slug_exists(new_slug, exclude_id=category_id):
                raise ValueError(f"Category with slug '{new_slug}' already exists")
            update_dict["slug"] = new_slug

        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(category_id)},
                {"$set": update_dict}
            )
        except InvalidId:
            return None
        if result.matched_count == 0:
            return None

        # Update blog posts that reference the old slug
        if old_slug and update_dict.get("slug") and old_slug != update_dict["slug"]:
            posts_col = get_collection("posts")
            await posts_col.update_many(
                {"categories": old_slug},
                {"$set": {"categories.$": update_dict["slug"]}}
            )

        return await self.get_by_id(category_id)

    async def delete(self, category_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(category_id)})
        except InvalidId:
            return False
        return result.deleted_count > 0


_category_service = None


def get_category_service() -> CategoryService:
    global _category_service
    if _category_service is None:
        _category_service = CategoryService()
    return _category_service
