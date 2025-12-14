from .basic_import import *
from models.posts import Post
from models.tags import Tag
from models.post_tags import PostTag
from models.savedPost import SavedPost
from models.comments import Comment
from models.likes import Like
from models.views import View
from slugify import slugify
from router.notification import notify_new_post
from fastapi import Query

router = APIRouter()

# ==============================
# Create Post
# ==============================
@router.post("/create-posts/")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    category_id: Optional[int] = Form(None),
    status: str = Form(...),
    tag_ids: Optional[List[int]] = Form([]),
    cover_image: UploadFile = File(None),
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    # Create slug
    slug = slugify(title)
    existing = db.query(Post).filter(Post.slug == slug).first()
    if existing:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    # Convert uploaded image to Base64
    base64_image = None
    if cover_image:
        file_bytes = await cover_image.read()
        base64_image = base64.b64encode(file_bytes).decode("utf-8")

    post = Post(
        title=title,
        slug=slug,
        content=content,
        cover_image=base64_image,
        category_id=category_id,
        author_id=current_user.id,
        status=status,
        published_at=datetime.utcnow() if status == "published" else None
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    # Add tags relation
    if tag_ids:
        for tag_id in tag_ids:
            db.add(PostTag(post_id=post.id, tag_id=tag_id))
        db.commit()

    notify_new_post(post, db)

    return {
        "message": "Post created successfully",
        "post": jsonable_encoder(post)
    }


# ==============================
# Get All Posts
# ==============================
@router.get("/all-posts/")
async def get_all_posts(db: Session = Depends(db_dependency),current_user: User = Depends(get_current_user)):
    posts = db.query(Post).filter(Post.status == "published").all()
    result = []

    for post in posts:
        post_id = post.id
        author = db.query(User).filter(User.id == post.author_id).first()

        # Like count
        like_count = db.query(Like).filter(Like.post_id == post_id).count()

        # Comment count
        comment_count = db.query(Comment).filter(Comment.post_id == post_id).count()
        view_count = db.query(View).filter(View.post_id == post_id).count()
        # Did current user like?
        user_liked = (
            db.query(Like)
            .filter(Like.post_id == post_id, Like.user_id == current_user.id)
            .first()
            is not None
        )
        # Saved by user?
        user_saved = (
            db.query(SavedPost)
            .filter(SavedPost.post_id == post_id, SavedPost.user_id == current_user.id)
            .first()
            is not None
        )

        # Did user comment?
        user_comments = (
            db.query(Comment)
            .filter(Comment.post_id == post_id, Comment.user_id == current_user.id)
            .all()
        )
        tags = [
            {"id": pt.tag.id, "name": pt.tag.name, "slug": pt.tag.slug} 
            for pt in post.tags
        ]

        result.append({
            "post": jsonable_encoder(post),
            "author_name": author.username if author else None,
            "author_image": author.profile_image if author else None,
            "stats": {
                "like_count": like_count,
                "comment_count": comment_count,
                "view_count": view_count
            },
            "user_activity": {
                "liked": user_liked,
                "saved": user_saved,
                "has_commented": len(user_comments) > 0,
                "comments": jsonable_encoder(user_comments)
            },
            "tags": tags,
            "tag_ids": [t["id"] for t in tags],
        })

    return result


@router.get("/posts-by-status/{status}/")
async def get_posts_by_status(status: str,db: Session = Depends(db_dependency),current_user: User = Depends(get_current_user)):
    posts = db.query(Post).filter(Post.status == status).all()
    result = []

    for post in posts:
        post_id = post.id
        author = db.query(User).filter(User.id == post.author_id).first()

        # Like count
        like_count = db.query(Like).filter(Like.post_id == post_id).count()

        # Comment count
        comment_count = db.query(Comment).filter(Comment.post_id == post_id).count()
        view_count = db.query(View).filter(View.post_id == post_id).count()

        # Did current user like?
        user_liked = (
            db.query(Like)
            .filter(Like.post_id == post_id, Like.user_id == current_user.id)
            .first()
            is not None
        )
        # Saved by user?
        user_saved = (
            db.query(SavedPost)
            .filter(SavedPost.post_id == post_id, SavedPost.user_id == current_user.id)
            .first()
            is not None
        )

        # Did user comment?
        user_comments = (
            db.query(Comment)
            .filter(Comment.post_id == post_id, Comment.user_id == current_user.id)
            .all()
        )
        tags = [
            {"id": pt.tag.id, "name": pt.tag.name, "slug": pt.tag.slug} 
            for pt in post.tags
        ]
        result.append({
            "post": jsonable_encoder(post),
            "author_name": author.username if author else None,
            "author_image": author.profile_image if author else None,            
            "stats": {
                "like_count": like_count,
                "comment_count": comment_count,
                "view_count": view_count
            },
            "tags": tags,
            "tag_ids": [t["id"] for t in tags],
            "user_activity": {
                "liked": user_liked,
                "saved": user_saved,
                "has_commented": len(user_comments) > 0,
                "comments": jsonable_encoder(user_comments)
            }
        })

    return result

@router.get("/get-all-posts-by-status-id/{user_id}/")
async def get_all_posts_by_status_and_user(
    user_id: int,
    status: Optional[List[str]] = Query(["draft", "published"]),  # default to draft & published
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user),
):
    # ---------------------------
    # 1️⃣ Authored posts filtered by status
    # ---------------------------
    authored_posts = (
        db.query(Post)
        .filter(Post.author_id == user_id, Post.status.in_(status))
        .order_by(Post.created_at.desc())
        .all()
    )

    def format_post(post):
        author = db.query(User).filter(User.id == post.author_id).first()
        like_count = db.query(Like).filter(Like.post_id == post.id).count()
        comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        view_count = db.query(View).filter(View.post_id == post.id).count()

        user_liked = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.id).first() is not None
        user_saved = db.query(SavedPost).filter(SavedPost.post_id == post.id, SavedPost.user_id == current_user.id).first() is not None
        user_comments = db.query(Comment).filter(Comment.post_id == post.id, Comment.user_id == current_user.id).all()
        tags = [
            {"id": pt.tag.id, "name": pt.tag.name, "slug": pt.tag.slug} 
            for pt in post.tags
        ]
        return {
            "post": jsonable_encoder(post),
            "author_name": author.username if author else None,
            "author_image": author.profile_image if author else None,
            "stats": {
                "like_count": like_count,
                "comment_count": comment_count,
                "view_count": view_count
            },
            "tags": tags,
            "tag_ids": [t["id"] for t in tags],
            "user_activity": {
                "liked": user_liked,
                "saved": user_saved,
                "has_commented": len(user_comments) > 0,
                "comments": jsonable_encoder(user_comments)
            }
        }

    return {
        "authored": [format_post(p) for p in authored_posts],
    }

@router.get("/get-saved-posts/{user_id}/")
async def get_saved_posts(user_id: int, db: Session = Depends(db_dependency)):
    saved = (
        db.query(SavedPost)
        .join(Post, SavedPost.post_id == Post.id)
        .filter(SavedPost.user_id == user_id)
        .order_by(Post.created_at.desc())
        .all()
    )

    result = []
    for sp in saved:
        post = sp.post
        author = db.query(User).filter(User.id == post.author_id).first()
        like_count = db.query(Like).filter(Like.post_id == post.id).count()
        comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        view_count = db.query(View).filter(View.post_id == post.id).count()
        tags = [
            {"id": pt.tag.id, "name": pt.tag.name, "slug": pt.tag.slug} 
            for pt in post.tags
        ]
        result.append({
            "post": jsonable_encoder(post),
            "author_name": author.username if author else None,
            "author_image": author.profile_image if author else None,
            "stats": {
                "like_count": like_count,
                "comment_count": comment_count,
                "view_count": view_count,
            },
            "tags": tags,
            "tag_ids": [t["id"] for t in tags],
            "user_activity": {
                "liked": False,
                "saved": True,
                "has_commented": False,
                "comments": []
            }
        })

    return result

# ==============================
# Get Post by ID
# ==============================
@router.get("/posts/{post_id}/")
async def get_post_by_id(post_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    author = db.query(User).filter(User.id == post.author_id).first()

    like_count = db.query(Like).filter(Like.post_id == post_id).count()
    comment_count = db.query(Comment).filter(Comment.post_id == post_id).count()
    view_count = db.query(View).filter(View.post_id == post_id).count()
    user_liked = (
        db.query(Like)
        .filter(Like.post_id == post_id, Like.user_id == current_user.id)
        .first()
        is not None
    )
    user_saved = (
        db.query(SavedPost)
        .filter(SavedPost.post_id == post_id, SavedPost.user_id == current_user.id)
        .first()
        is not None
    )

    # All user comments (if they commented)
    user_comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id, Comment.user_id == current_user.id)
        .all()
    )
    tags = [
        {
            "id": pt.tag.id,
            "name": pt.tag.name,
            "slug": pt.tag.slug
        }
        for pt in post.tags
    ]
    return {
        "post": jsonable_encoder(post),
        "author_name": author.username if author else None,
        "author_image": author.profile_image if author else None,        
        "tags": tags,         # <---- TAGS ADDED HERE
        "tag_ids": [t["id"] for t in tags], 
        "stats": {
            "like_count": like_count,
            "comment_count": comment_count,
            "view_count": view_count
        },
        "user_activity": {
            "liked": user_liked,
            "saved": user_saved,
            "comments": jsonable_encoder(user_comments),
            "has_commented": len(user_comments) > 0
        }
    }
    # return jsonable_encoder(post)

# ==============================
# Update Post
# ==============================

def generate_unique_slug(db: Session, title: str, post_id: int):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1

    while (
        db.query(Post)
        .filter(Post.slug == slug, Post.id != post_id)
        .first()
    ):
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

@router.put("/update-posts/{post_id}/")
async def update_post(
    post_id: int,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    status: Optional[str] = Form(None),
    tag_ids: Optional[List[int]] = Form(None),
    cover_image: UploadFile = File(None),
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        # ===== Update fields =====
        if title is not None:
            post.title = title
            post.slug = generate_unique_slug(db, title, post_id)

        if content is not None:
            post.content = content

        if category_id is not None:
            post.category_id = category_id

        if status is not None:
            post.status = status
            if status == "published":
                post.published_at = datetime.utcnow()

        if cover_image:
            file_bytes = await cover_image.read()
            post.cover_image = base64.b64encode(file_bytes).decode("utf-8")

        if tag_ids is not None:
            db.query(PostTag).filter(PostTag.post_id == post_id).delete()
            for tag in tag_ids:
                db.add(PostTag(post_id=post_id, tag_id=tag))

        db.commit()
        db.refresh(post)

        return {
            "message": "Post updated successfully",
            "post": jsonable_encoder(post),
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A post with this title already exists. Please choose a different title."
        )

# ==============================
# Delete Post
# ==============================
@router.delete("/delete-posts/{post_id}/")
async def delete_post(post_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}


@router.get("/api/search")
def search(query: str = Query(..., min_length=1), db: Session = Depends(db_dependency)):
    # Remove leading # if present
    search_query = query[1:] if query.startswith("#") else query

    # Search posts by title OR tag name
    posts_by_title = db.query(Post).filter(Post.title.ilike(f"%{search_query}%"))
    posts_by_tag = db.query(Post).join(PostTag).join(Tag).filter(Tag.name.ilike(f"%{search_query}%"))
    posts = posts_by_title.union(posts_by_tag).all()

    # Search users
    users = db.query(User).filter(
        (User.username.ilike(f"%{search_query}%")) | (User.email.ilike(f"%{search_query}%"))
    ).all()

    # Search tags only if query starts with #
    tags = []
    if query.startswith("#"):
        tags = db.query(Tag).filter(Tag.name.ilike(f"%{search_query}%")).all()

    return {
        "posts": [
            {
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "author": p.author.username,
                "cover_image": p.cover_image,
                "content": p.content,
                "category": p.category.name if p.category else None,
                "tags": [{"id": t.tag.id, "name": t.tag.name, "slug": t.tag.slug} for t in p.tags]
            }
            for p in posts
        ],
        "users": [
            {"id": u.id, "username": u.username, "email": u.email, "profile_image": u.profile_image}
            for u in users
        ],
        "tags": [
            {"id": t.id, "name": t.name, "slug": t.slug} for t in tags
        ]
    }
