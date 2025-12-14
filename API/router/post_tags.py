from .basic_import import *
from models.tags import Tag
from models.post_tags import PostTag
from models.posts import Post
from models.users import User
from router.auth import get_current_user


router = APIRouter()


# 1️⃣ Get all tags that are used in posts
@router.get("/tags/used/")
async def get_used_tags(
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    tags = (
        db.query(Tag)
        .join(PostTag, Tag.id == PostTag.tag_id)
        .distinct()
        .all()
    )
    return jsonable_encoder(tags)


# 2️⃣ Get tags with their usage count
@router.get("/tags/used-count/")
async def get_used_tags_with_count(
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    results = (
        db.query(Tag.id, Tag.name, func.count(PostTag.post_id).label("post_count"))
        .join(PostTag, Tag.id == PostTag.tag_id)
        .group_by(Tag.id, Tag.name)
        .all()
    )
    return [
        {"id": r.id, "name": r.name, "post_count": r.post_count}
        for r in results
    ]


# 3️⃣ Get tags for a specific post
@router.get("/posts/{post_id}/tags/")
async def get_post_tags(
    post_id: int,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # post.tags is a list of PostTag objects
    return [pt.tag.name for pt in post.tags]


# 4️⃣ Get all posts for a given tag name
@router.get("/posts/by-tag-name/{tag_name}")
async def get_posts_by_tag_name(
    tag_name: str,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    try:
        tag = db.query(Tag).filter(Tag.name.ilike(tag_name)).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        # Join through PostTag to get related posts
        posts = (
            db.query(Post)
            .join(PostTag, Post.id == PostTag.post_id)
            .filter(PostTag.tag_id == tag.id)
            .all()
        )

        if not posts:
            return {"tag": tag.name, "posts": []}

        result = [
            {
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "content": post.content,
                "cover_image": post.cover_image,
                "author": post.author.username if post.author else None,
                "category": post.category.name if post.category else None,
                "created_at": post.created_at,
                "tags": [t.tag.name for t in post.tags],
                "likes_count": len(post.likes),
                "comments_count": len(post.comments),
            }
            for post in posts
        ]

        return {"tag": tag.name, "posts": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
