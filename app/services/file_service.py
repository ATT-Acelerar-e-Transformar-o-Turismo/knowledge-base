import os
import uuid
import aiofiles
import logging
from typing import Dict, Set
from datetime import datetime, timezone
from fastapi import UploadFile
import mimetypes

from app.config import settings
from app.exceptions import (
    FileUploadError,
    InvalidFileTypeError,
    FileSizeLimitExceededError,
    file_upload_failed,
    invalid_file_type,
    file_size_exceeded
)

logger = logging.getLogger(__name__)


class FileService:
    """Service for handling file uploads, validation, and storage."""

    def __init__(self) -> None:
        self._upload_dir = settings.UPLOAD_DIR
        self._max_file_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024

        self._allowed_image_types: Set[str] = set(
            settings.ALLOWED_IMAGE_TYPES.split(",")
        )
        self._allowed_document_types: Set[str] = set(
            settings.ALLOWED_DOCUMENT_TYPES.split(",")
        )

        os.makedirs(os.path.join(self._upload_dir, "thumbnails"), exist_ok=True)
        os.makedirs(os.path.join(self._upload_dir, "attachments"), exist_ok=True)

    def _generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate UUID-based unique filename preserving original extension."""
        name, ext = os.path.splitext(original_filename)
        unique_id = str(uuid.uuid4())
        return f"{prefix}{unique_id}{ext}" if prefix else f"{unique_id}{ext}"

    def _get_file_info(self, file: UploadFile) -> Dict[str, str]:
        """Extract file metadata including MIME type detection."""
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        return {
            "original_filename": file.filename,
            "mime_type": mime_type,
            "size": "0"
        }

    async def save_file(self, file: UploadFile, subdirectory: str) -> Dict[str, any]:
        """Save uploaded file with validation and return metadata."""
        if file.size and file.size > self._max_file_size:
            raise file_size_exceeded(settings.MAX_FILE_SIZE_MB)

        file_info = self._get_file_info(file)
        unique_filename = self._generate_filename(file.filename)
        file_path = os.path.join(self._upload_dir, subdirectory, unique_filename)

        try:
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)
                file_info["size"] = str(len(content))
        except (IOError, OSError) as e:
            logger.error(f"Failed to save file {unique_filename}: {e}")
            raise file_upload_failed(str(e))

        file_url = f"/uploads/{subdirectory}/{unique_filename}"

        return {
            "filename": unique_filename,
            "original_filename": file_info["original_filename"],
            "url": file_url,
            "size": int(file_info["size"]),
            "mime_type": file_info["mime_type"],
            "uploaded_at": datetime.now(timezone.utc)
        }

    async def upload_thumbnail(self, file: UploadFile) -> Dict[str, any]:
        """Upload and validate thumbnail image file."""
        file_info = self._get_file_info(file)

        if file_info["mime_type"] not in self._allowed_image_types:
            raise invalid_file_type("JPEG, PNG, GIF, WebP")

        return await self.save_file(file, "thumbnails")

    async def upload_attachment(self, file: UploadFile) -> Dict[str, any]:
        """Upload and validate document attachment file."""
        file_info = self._get_file_info(file)

        all_allowed_types = self._allowed_image_types | self._allowed_document_types
        if file_info["mime_type"] not in all_allowed_types:
            raise invalid_file_type("PDF, Word, Excel, Images, Text files")

        return await self.save_file(file, "attachments")

    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage if it exists."""
        try:
            full_path = os.path.join(self._upload_dir, file_path.lstrip("/uploads/"))
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        except (IOError, OSError, PermissionError) as e:
            logger.warning(f"Failed to delete file {file_path}: {e}")
        return False

    def get_file_path(self, file_url: str) -> str:
        """Convert file URL to absolute filesystem path."""
        if file_url.startswith("/uploads/"):
            file_url = file_url[9:]
        return os.path.join(self._upload_dir, file_url)


file_service = FileService()