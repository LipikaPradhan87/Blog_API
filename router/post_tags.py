from .basic_import import *
from models.tags import Tag
from models.post_tags import Post_tag
from models.posts import Post
from typing import List, Optional
from fastapi import Body
import bcrypt
from pydantic import BaseModel


router = APIRouter()

@router.get("/tags/used/")
async def get_used_tags(db: Session = Depends(db_dependency)):
    tags = (
        db.query(Tag)
        .join(Post_tag, Tag.id == Post_tag.tagId).distinct().all())
    return jsonable_encoder(tags)

@router.get("/tags/used-count/")
async def get_used_tags_with_count(db: Session = Depends(db_dependency)):
    results = (
        db.query(Tag.id, Tag.name, func.count(Post_tag.id).label("post_count"))
        .join(Post_tag, Tag.id == Post_tag.tagId)
        .group_by(Tag.id, Tag.name).all()
    )
    return [{"id": r.id, "name": r.name, "post_count": r.post_count} for r in results]


@router.get("/posts/{post_id}/tags/")
async def get_post_tags(post_id: int, db: Session = Depends(db_dependency)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return [tag.name for tag in post.tags]

@router.get("/posts/by-tag-name/{tag_name}")
async def get_posts_by_tag_name(tag_name: str, db: Session = Depends(db_dependency)):
    try:
        # Find tag by name (case-insensitive)
        tag = db.query(Tag).filter(Tag.name.ilike(tag_name)).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        # Explicitly join posts via association table to avoid lazy loading issues
        posts = (
            db.query(Post)
            .join(Post.tags)
            .filter(Tag.id == tag.id)
            .all()
        )

        if not posts:
            return {"tag": tag.name, "posts": []}

        # Format the response
        result = [
            {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "image": post.image,
                "author": post.author.username if post.author else None,
                "category": post.category.name if post.category else None,
                "created_at": post.created_at,
                "tags": [t.name for t in post.tags],
                "likes_count": len(post.likes),
                "comments_count": len(post.comments)
            }
            for post in posts
        ]

        return {"tag": tag.name, "posts": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

