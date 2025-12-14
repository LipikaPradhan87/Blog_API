from .basic_import import *
from models.comments import Comment
from models.posts import Post
from models.users import User
from router.notification import notify_comment

router = APIRouter()


# ==============================
# Schemas
# ==============================
class PostCommentRequest(BaseModel):
    content: str
    parent_id: Optional[int] = None  # for replies


class UpdateCommentRequest(BaseModel):
    content: str


# ==============================
# Add Comment or Reply
# ==============================
@router.post("/posts/{post_id}/comments/")
async def add_comment(
    post_id: int,
    request: PostCommentRequest,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    # Ensure post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # If replying to another comment, validate parent exists
    if request.parent_id:
        parent = db.query(Comment).filter(Comment.id == request.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")
    parent_id = request.parent_id if request.parent_id not in [0, "0"] else None

    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=request.content,
        parent_id=parent_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Notify post owner
    notify_comment(comment, db)

    return {
        "message": "Comment added successfully",
        "comment_id": comment.id,
        "parent_id": comment.parent_id,
    }


# ==============================
# Get Comments (with nested replies)
# ==============================
def serialize_comment(comment: Comment):
    replies = comment.replies or []
    sorted_replies = sorted(replies, key=lambda r: r.created_at)

    return {
        "id": comment.id,
        "user_id": comment.user_id,
        "username": comment.user.username if comment.user else None,
        "content": comment.content,
        "created_at": comment.created_at,
        "parent_id": comment.parent_id,
        "replies": [serialize_comment(r) for r in sorted_replies],
    }


@router.get("/posts/{post_id}/comments/")
async def get_comments(post_id: int, db: Session = Depends(db_dependency)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Only fetch top-level comments
    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id, Comment.parent_id.is_(None))
        .order_by(Comment.created_at.desc())
        .all()
    )

    return [serialize_comment(c) for c in comments]

@router.get("/comment-by-id/{comment_id}")
async def get_comment_by_id( comment_id: int,db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return jsonable_encoder(comment)
# ==============================
# Update Comment
# ==============================
@router.put("/update-comments/{comment_id}/")
async def update_comment(comment_id: int, request: UpdateCommentRequest,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    comment.content = request.content
    db.commit()
    db.refresh(comment)

    return {
        "message": "Comment updated successfully",
        "comment": {
            "id": comment.id,
            "content": comment.content,
        },
    }


# ==============================
# Delete Comment (and its replies)
# ==============================
@router.delete("/delete-comments/{comment_id}/")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}
