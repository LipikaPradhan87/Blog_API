from .basic_import import *
from models.comments import Comment
from models.posts import Post
from router.notification import notify_comment

router = APIRouter()

class PostCommentRequest(BaseModel):
    content: str
    user_id: int

class UpdateCommentRequest(BaseModel):
    content: Optional[str] = None


@router.post("/posts/{post_id}/comments/")
async def add_comment(post_id: int, request: PostCommentRequest, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        post_id=post_id,
        user_id=request.user_id,
        content=request.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    notify_comment(comment, db)
    return {"message": "Comment added successfully", "comment_id": comment.id}
    
@router.get("/posts/{post_id}/comments/")
async def get_comments(post_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return [
        {
            "id": c.id,
            "user_id": c.user_id,
            "username": c.user.username if c.user else None,
            "content": c.content,
            "created_at": c.created_at
        } for c in comments
    ]   
    
@router.put("/comments/{comment_id}/")
async def update_comment(comment_id: int, request: UpdateCommentRequest, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.content = request.content
    db.commit()
    db.refresh(comment)
    return {"message": "Comment updated successfully", "comment": {
        "id": comment.id,
        "user_id": comment.user_id,
        "content": comment.content
    }}

# Delete comment
# ===============================
@router.delete("/comments/{comment_id}/")
async def delete_comment(comment_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

