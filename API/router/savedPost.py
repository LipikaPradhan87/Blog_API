from .basic_import import *
from models.savedPost import SavedPost
from models.posts import Post

router = APIRouter()

@router.post("/posts/{post_id}/save/")
async def save_post(post_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = db.query(SavedPost).filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Post already saved")

    saved = SavedPost(user_id=current_user.id, post_id=post_id)
    db.add(saved)
    db.commit()
    return {"message": "Post saved successfully"}

@router.delete("/posts/{post_id}/unsave/")
async def unsave_post(post_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    saved = db.query(SavedPost).filter_by(user_id=current_user.id, post_id=post_id).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Post not saved")

    db.delete(saved)
    db.commit()
    return {"message": "Post unsaved successfully"}

@router.get("/saved-posts/")
async def get_saved_posts(db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    saved_posts = db.query(SavedPost).filter(SavedPost.user_id == current_user.id).all()
    return jsonable_encoder(saved_posts)
