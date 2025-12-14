from .basic_import import *
from models.notification import Notification
from models.users import User
from models.posts import Post
from models.comments import Comment
from models.likes import Like
from router.auth import get_current_user


router = APIRouter()

# ------------------------------------------------------------
# 📢 Helper functions to create notifications
# ------------------------------------------------------------
def notify_new_post(new_post, db: Session):
    """Notify all other users when a new post is published."""
    users = db.query(User).filter(User.id != new_post.author_id).all()
    for user in users:
        notif = Notification(
            user_id=user.id,          # recipient
            sender_id=new_post.author_id,  # sender
            post_id=new_post.id,
            message=f"New post published: '{new_post.title}'"
        )
        db.add(notif)
    db.commit()


def notify_like(post_like: Like, db: Session):
    """Notify post author when someone likes their post."""
    post = db.query(Post).filter(Post.id == post_like.post_id).first()
    notif = Notification(
        user_id=post.author_id,
        sender_id=post_like.user_id,
        post_id=post.id,
        message=f"{post_like.user.username if post_like.user else 'Someone'} liked your post '{post.title}'"
    )
    db.add(notif)
    db.commit()


def notify_comment(comment: Comment, db: Session):
    """Notify post author when someone comments on their post."""
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    notif = Notification(
        user_id=post.author_id,
        sender_id=comment.user_id,
        post_id=post.id,
        comment_id=comment.id,
        message=f"{comment.user.username if comment.user else 'Someone'} commented on your post '{post.title}'"
    )
    db.add(notif)
    db.commit()


# ------------------------------------------------------------
# 📬 API Endpoints
# ------------------------------------------------------------

@router.get("/notifications/{user_id}/")
async def get_notifications(
    user_id: int,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    """Fetch all notifications for a user."""
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return [
        {
            "id": n.id,
            "message": n.message,
            "sender": n.sender.username if n.sender else None,
            "post_id": n.post_id,
            "comment_id": n.comment_id,
            "is_read": bool(n.is_read),
            "created_at": n.created_at
        }
        for n in notifications
    ]

@router.get("/notification-count/{user_id}/")
async def get_notification_count( user_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    unread_count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .count()
    )
    return {
        "count": len(notifications),
        "unread_count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at
            }
            for n in notifications
        ]
    }

@router.patch("/notifications/{notif_id}/read/")
async def mark_notification_read(
    notif_id: int,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read."""
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = 1  # mark as read
    db.commit()
    db.refresh(notif)

    return {"message": "Notification marked as read", "id": notif.id}

@router.patch("/notifications/read-all/")
async def mark_all_notifications_read(
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    """Mark all unread notifications for the current user as read."""
    
    # Fetch all unread notifications for the current user
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == 0
    ).all()
    
    if not unread_notifications:
        return {"message": "No unread notifications found."}
    
    # Mark all as read
    for notif in unread_notifications:
        notif.is_read = 1
    
    db.commit()
    
    return {
        "message": "All unread notifications marked as read",
        "count": len(unread_notifications)
    }
