from .basic_import import *
from models.likes import Like
from models.posts import Post
from router.notification import notify_like
from models.notification import Notification

router = APIRouter()


# ==============================
# Like a Post
# ==============================
@router.post("/posts/{post_id}/like/")
async def like_post( post_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # # Prevent user from liking their own post
    # if post.author_id == current_user.id:
    #     raise HTTPException(status_code=400, detail="You cannot like your own post")

    # Check if already liked
    existing_like = (
        db.query(Like)
            .filter(Like.post_id == post_id, Like.user_id == current_user.id)
            .first()
    )
    if existing_like:
        raise HTTPException(status_code=400, detail="You have already liked this post")

    # Add new like
    like = Like(post_id=post_id, user_id=current_user.id)
    db.add(like)  
    db.commit()
    db.refresh(like)
    notify_like(like, db)

    return {"message": "Post liked successfully", "like_id": like.id}


# ==============================
# Unlike a Post
# ==============================
@router.delete("/posts/{post_id}/unlike/")
async def unlike_post(
    post_id: int,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    like = (
        db.query(Like)
        .filter(Like.post_id == post_id, Like.user_id == current_user.id)
        .first()
    )
    if not like:
        raise HTTPException(status_code=404, detail="You haven’t liked this post")

    db.delete(like)
    # db.query(Notification).filter(
    #     Notification.post_id == post_id,
    #     Notification.sender_id == current_user.id,
    #     Notification.message.like("%liked your post%")
    # ).delete()    
    db.commit()

    return {"message": "Post unliked successfully"}


# ==============================
# Get All Likes for a Post
# ==============================
@router.get("/posts/{post_id}/likes/")
async def get_post_likes(
    post_id: int,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes = db.query(Like).filter(Like.post_id == post_id).all()

    return {
        "post_id": post_id,
        "likes_count": len(likes),
        "users": [
            {
                "user_id": like.user_id,
                "username": like.user.username if like.user else None,
                "liked_at": like.created_at
            }
            for like in likes
        ],
    }
