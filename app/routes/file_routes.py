from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
import os
from app.services.file_service import file_service
from app.exceptions import InvalidFileTypeError, FileSizeLimitExceededError
from app.auth import require_admin

router = APIRouter(prefix="/uploads", tags=["files"])


@router.get("/thumbnails/{filename}")
async def serve_thumbnail(filename: str):
    """Serve thumbnail images"""
    file_path = file_service.get_file_path(f"thumbnails/{filename}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)


@router.get("/attachments/{filename}")
async def serve_attachment(filename: str):
    """Serve attachment files"""
    file_path = file_service.get_file_path(f"attachments/{filename}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)


@router.post("/domain-icons/upload")
async def upload_domain_icon(file: UploadFile = File(...), _=Depends(require_admin)):
    """Upload domain icon image"""
    try:
        result = await file_service.upload_domain_icon(file)
        return result
    except (InvalidFileTypeError, FileSizeLimitExceededError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/domain-icons/{filename}")
async def serve_domain_icon(filename: str):
    """Serve domain icon images"""
    file_path = file_service.get_file_path(f"domain-icons/{filename}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@router.delete("/domain-icons/{filename}")
async def delete_domain_icon(filename: str, _=Depends(require_admin)):
    """Delete domain icon"""
    success = await file_service.delete_domain_icon(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "Icon deleted successfully"}


@router.post("/domain-images/upload")
async def upload_domain_image(file: UploadFile = File(...), _=Depends(require_admin)):
    """Upload domain image"""
    try:
        result = await file_service.upload_domain_image(file)
        return result
    except (InvalidFileTypeError, FileSizeLimitExceededError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/domain-images/{filename}")
async def serve_domain_image(filename: str):
    """Serve domain image files"""
    file_path = file_service.get_file_path(f"domain-images/{filename}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@router.delete("/domain-images/{filename}")
async def delete_domain_image(filename: str, _=Depends(require_admin)):
    """Delete domain image"""
    success = await file_service.delete_domain_image(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "Image deleted successfully"}