from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File, Form
from typing import List, Optional
from app.models.blog_post import BlogPost, BlogPostCreate, BlogPostUpdate
from app.services.blog_service import get_blog_service
from app.services.file_service import file_service

router = APIRouter(prefix="/api/blog", tags=["blog"])


# Public endpoints
@router.get("/posts", response_model=List[BlogPost])
async def get_published_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50)
):
    """Get published blog posts for public view"""
    blog_service = get_blog_service()
    return await blog_service.get_published_posts(skip=skip, limit=limit)


@router.get("/posts/{post_id}", response_model=BlogPost)
async def get_post(post_id: str):
    """Get a specific blog post and increment view count"""
    blog_service = get_blog_service()
    post = await blog_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Only increment view count for published posts
    if post.status == "published":
        await blog_service.increment_view_count(post_id)

    return post


# Admin endpoints
@router.get("/admin/posts", response_model=List[BlogPost])
async def get_all_posts_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50)
):
    """Get all blog posts for admin view"""
    blog_service = get_blog_service()
    return await blog_service.get_all_posts(skip=skip, limit=limit)


@router.post("/admin/posts", response_model=BlogPost)
async def create_post(post: BlogPostCreate):
    """Create a new blog post"""
    blog_service = get_blog_service()
    return await blog_service.create_post(post)


@router.put("/admin/posts/{post_id}", response_model=BlogPost)
async def update_post(post_id: str, update_data: BlogPostUpdate):
    """Update a blog post"""
    blog_service = get_blog_service()
    post = await blog_service.update_post(post_id, update_data)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.delete("/admin/posts/{post_id}")
async def delete_post(post_id: str):
    """Delete a blog post"""
    blog_service = get_blog_service()
    success = await blog_service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}


@router.post("/admin/posts/{post_id}/thumbnail")
async def upload_thumbnail(post_id: str, file: UploadFile = File(...)):
    """Upload thumbnail image for a blog post"""
    # Check if post exists
    blog_service = get_blog_service()
    post = await blog_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Upload thumbnail
    file_info = await file_service.upload_thumbnail(file)

    # Update post with thumbnail URL
    success = await blog_service.set_thumbnail(post_id, file_info["url"])
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update post with thumbnail")

    return {"message": "Thumbnail uploaded successfully", "thumbnail_url": file_info["url"]}


@router.post("/admin/posts/{post_id}/attachments")
async def upload_attachment(post_id: str, file: UploadFile = File(...)):
    """Upload file attachment for a blog post"""
    # Check if post exists
    blog_service = get_blog_service()
    post = await blog_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Upload attachment
    file_info = await file_service.upload_attachment(file)

    # Add attachment to post
    success = await blog_service.add_attachment(post_id, file_info)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add attachment to post")

    return {"message": "Attachment uploaded successfully", "attachment": file_info}


@router.delete("/admin/posts/{post_id}/attachments/{filename}")
async def remove_attachment(post_id: str, filename: str):
    """Remove file attachment from a blog post"""
    # Remove from post
    blog_service = get_blog_service()
    success = await blog_service.remove_attachment(post_id, filename)
    if not success:
        raise HTTPException(status_code=404, detail="Post or attachment not found")

    # Delete file
    await file_service.delete_file(f"attachments/{filename}")

    return {"message": "Attachment removed successfully"}


@router.post("/admin/upload/thumbnail")
async def upload_thumbnail_standalone(file: UploadFile = File(...)):
    """Upload thumbnail image (standalone)"""
    file_info = await file_service.upload_thumbnail(file)
    return {"message": "Thumbnail uploaded successfully", "file_info": file_info}


@router.post("/admin/upload/attachment")
async def upload_attachment_standalone(file: UploadFile = File(...)):
    """Upload attachment file (standalone)"""
    file_info = await file_service.upload_attachment(file)
    return {"message": "Attachment uploaded successfully", "file_info": file_info}