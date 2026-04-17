from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
from app.models.author import Author, AuthorCreate, AuthorUpdate
from app.services.author_service import get_author_service
from app.services.file_service import file_service
from app.auth import require_admin

router = APIRouter(prefix="/api/blog/authors", tags=["authors"])


@router.get("", response_model=List[Author])
async def get_all_authors():
    service = get_author_service()
    return await service.get_all()


@router.get("/slug/{slug}", response_model=Author)
async def get_author_by_slug(slug: str):
    service = get_author_service()
    author = await service.get_by_slug(slug)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.get("/{author_id}", response_model=Author)
async def get_author(author_id: str):
    service = get_author_service()
    author = await service.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.post("", response_model=Author)
async def create_author(data: AuthorCreate, _=Depends(require_admin)):
    service = get_author_service()
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{author_id}", response_model=Author)
async def update_author(author_id: str, data: AuthorUpdate, _=Depends(require_admin)):
    service = get_author_service()
    try:
        author = await service.update(author_id, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.post("/{author_id}/photo")
async def upload_author_photo(author_id: str, file: UploadFile = File(...), _=Depends(require_admin)):
    service = get_author_service()
    author = await service.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    file_info = await file_service.upload_thumbnail(file)
    await service.set_photo(author_id, file_info["url"])
    return {"message": "Photo uploaded", "photo_url": file_info["url"]}


@router.post("/{author_id}/cover")
async def upload_author_cover(author_id: str, file: UploadFile = File(...), _=Depends(require_admin)):
    service = get_author_service()
    author = await service.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    file_info = await file_service.upload_thumbnail(file)
    await service.set_cover(author_id, file_info["url"])
    return {"message": "Cover uploaded", "cover_url": file_info["url"]}


@router.delete("/{author_id}")
async def delete_author(author_id: str, _=Depends(require_admin)):
    service = get_author_service()
    success = await service.delete(author_id)
    if not success:
        raise HTTPException(status_code=404, detail="Author not found")
    return {"message": "Author deleted"}
