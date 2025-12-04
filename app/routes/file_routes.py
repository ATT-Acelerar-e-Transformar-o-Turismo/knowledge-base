from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from app.services.file_service import file_service

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