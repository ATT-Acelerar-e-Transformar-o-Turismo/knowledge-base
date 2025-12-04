import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import Optional
import mimetypes
from datetime import datetime


class FileService:
    def __init__(self):
        self.upload_dir = "app/uploads"
        self.allowed_image_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        self.allowed_document_types = {
            "application/pdf", "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain", "text/csv"
        }
        self.max_file_size = 50 * 1024 * 1024  # 50MB

        # Create upload directories
        os.makedirs(os.path.join(self.upload_dir, "thumbnails"), exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, "attachments"), exist_ok=True)

    def _generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate unique filename while preserving extension"""
        name, ext = os.path.splitext(original_filename)
        unique_id = str(uuid.uuid4())
        return f"{prefix}{unique_id}{ext}" if prefix else f"{unique_id}{ext}"

    def _get_file_info(self, file: UploadFile) -> dict:
        """Get file information"""
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        return {
            "original_filename": file.filename,
            "mime_type": mime_type,
            "size": 0  # Will be updated after saving
        }

    async def save_file(self, file: UploadFile, subdirectory: str) -> dict:
        """Save uploaded file and return file information"""
        # Validate file size
        if file.size and file.size > self.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")

        file_info = self._get_file_info(file)

        # Generate unique filename
        unique_filename = self._generate_filename(file.filename)
        file_path = os.path.join(self.upload_dir, subdirectory, unique_filename)

        # Save file
        try:
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)
                file_info["size"] = len(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

        # Generate URL (relative path for now)
        file_url = f"/uploads/{subdirectory}/{unique_filename}"

        return {
            "filename": unique_filename,
            "original_filename": file_info["original_filename"],
            "url": file_url,
            "size": file_info["size"],
            "mime_type": file_info["mime_type"],
            "uploaded_at": datetime.utcnow()
        }

    async def upload_thumbnail(self, file: UploadFile) -> dict:
        """Upload thumbnail image"""
        file_info = self._get_file_info(file)

        # Validate image type
        if file_info["mime_type"] not in self.allowed_image_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid image type. Allowed: JPEG, PNG, GIF, WebP"
            )

        return await self.save_file(file, "thumbnails")

    async def upload_attachment(self, file: UploadFile) -> dict:
        """Upload document attachment"""
        file_info = self._get_file_info(file)

        # Validate document type
        all_allowed_types = self.allowed_image_types | self.allowed_document_types
        if file_info["mime_type"] not in all_allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Allowed: PDF, Word, Excel, Images, Text files"
            )

        return await self.save_file(file, "attachments")

    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            full_path = os.path.join(self.upload_dir, file_path.lstrip("/uploads/"))
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        except Exception:
            pass
        return False

    def get_file_path(self, file_url: str) -> str:
        """Get full file path from URL"""
        # Remove /uploads/ prefix if present
        if file_url.startswith("/uploads/"):
            file_url = file_url[9:]  # Remove "/uploads/" (9 characters)
        return os.path.join(self.upload_dir, file_url)

file_service = FileService()