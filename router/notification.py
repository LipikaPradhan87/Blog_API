from .basic_import import *
from models.notification import Notification
from models.users import User
from models.posts import Post
from models.comments import Comment
from models.likes import PostLike
from typing import List, Optional
from fastapi import Body
import bcrypt
from pydantic import BaseModel



router = APIRouter()

def notify_new_post(new_post, db: Session):
    users = db.query(User).filter(User.id != new_post.author_id).all()
    for user in users:
        notif = Notification(
            user_id=user.id,
            actor_id=new_post.author_id,
            type="post",
            post_id=new_post.id
        )
        db.add(notif)
    db.commit()

def notify_like(post_like: PostLike, db: Session):
    post = db.query(Post).filter(Post.id == post_like.post_id).first()
    if post.author_id != post_like.user_id:
        notif = Notification(
            user_id=post.author_id,
            actor_id=post_like.user_id,
            type="like",
            post_id=post.id
        )
        db.add(notif)
        db.commit()

def notify_comment(comment: Comment, db: Session):
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    if post.author_id != comment.user_id:
        notif = Notification(
            user_id=post.author_id,
            actor_id=comment.user_id,
            type="comment",
            post_id=post.id,
            comment_id=comment.id
        )
        db.add(notif)
        db.commit()

@router.get("/notifications/{user_id}/")
async def get_notifications(user_id: int, db: Session = Depends(db_dependency)):
    notifications = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
    return [
        {
            "id": n.id,
            "type": n.type,
            "actor": n.actor.username if n.actor else None,
            "post_id": n.post_id,
            "comment_id": n.comment_id,
            "is_read": n.is_read,
            "created_at": n.created_at
        } for n in notifications
    ]

@router.patch("/notifications/{notif_id}/read/")
async def mark_notification_read(notif_id: int, db: Session = Depends(db_dependency)):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}
