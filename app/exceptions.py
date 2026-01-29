from fastapi import HTTPException, status


class KnowledgeBaseException(Exception):
    """Base exception for knowledge-base service."""
    pass


class DatabaseConnectionError(KnowledgeBaseException):
    """Raised when database connection fails or is not initialized."""
    pass


class BlogPostNotFoundError(KnowledgeBaseException):
    """Raised when a blog post is not found."""
    pass


class FileUploadError(KnowledgeBaseException):
    """Raised when file upload fails."""
    pass


class InvalidFileTypeError(KnowledgeBaseException):
    """Raised when uploaded file type is not allowed."""
    pass


class FileSizeLimitExceededError(KnowledgeBaseException):
    """Raised when uploaded file exceeds size limit."""
    pass


class InvalidObjectIdError(KnowledgeBaseException):
    """Raised when an invalid MongoDB ObjectId is provided."""
    pass


def blog_post_not_found(post_id: str) -> HTTPException:
    """Create HTTPException for blog post not found."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Blog post with id {post_id} not found"
    )


def file_upload_failed(detail: str) -> HTTPException:
    """Create HTTPException for file upload failure."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"File upload failed: {detail}"
    )


def invalid_file_type(allowed_types: str) -> HTTPException:
    """Create HTTPException for invalid file type."""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid file type. Allowed types: {allowed_types}"
    )


def file_size_exceeded(max_size_mb: int) -> HTTPException:
    """Create HTTPException for file size exceeded."""
    return HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail=f"File too large. Maximum size: {max_size_mb}MB"
    )
