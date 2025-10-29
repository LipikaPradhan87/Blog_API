from .basic_import import *
from models.likes import PostLike
from models.posts import Post
from router.notification import notify_like

router = APIRouter()


class LikeRequest(BaseModel):
    user_id: int


@router.post("/posts/{post_id}/like/")
async def like_post(post_id: int, request: LikeRequest, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if user already liked the post
    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == request.user_id
    ).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="User already liked this post")

    # ✅ Add new like
    like = PostLike(post_id=post_id, user_id=request.user_id)
    print(like,"kkk")
    db.add(like)
    db.commit()
    db.refresh(like)

    notify_like(like, db)

    return {"message": "Post liked successfully", "like_id": like.id}


@router.delete("/posts/{post_id}/unlike/{user_id}/")
async def unlike_post(post_id: int, user_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == user_id
    ).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()
    return {"message": "Post unliked successfully"}

@router.get("/posts/{post_id}/likes/")
async def get_post_likes(post_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    likes = db.query(PostLike).filter(PostLike.post_id == post_id).all()
    return {
        "post_id": post_id,
        "likes_count": len(likes),
        "users": [{"user_id": l.user_id, "username": l.user.username} for l in likes]
    }