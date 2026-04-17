from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.category import Category, CategoryCreate, CategoryUpdate
from app.services.category_service import get_category_service
from app.auth import require_admin

router = APIRouter(prefix="/api/blog/categories", tags=["categories"])


@router.get("", response_model=List[Category])
async def get_all_categories():
    service = get_category_service()
    return await service.get_all()


@router.get("/type/{type}", response_model=List[Category])
async def get_categories_by_type(type: str):
    service = get_category_service()
    return await service.get_by_type(type)


@router.post("", response_model=Category)
async def create_category(data: CategoryCreate, _=Depends(require_admin)):
    service = get_category_service()
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{category_id}", response_model=Category)
async def update_category(category_id: str, data: CategoryUpdate, _=Depends(require_admin)):
    service = get_category_service()
    try:
        category = await service.update(category_id, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}")
async def delete_category(category_id: str, _=Depends(require_admin)):
    service = get_category_service()
    success = await service.delete(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}
