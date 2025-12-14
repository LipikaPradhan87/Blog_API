from .basic_import import *
from models.views import View
from models.posts import Post

router = APIRouter()

@router.post("/posts/{post_id}/view/")
async def record_view(post_id: int, request: Request, db: Session = Depends(db_dependency), current_user: Optional[User] = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    ip = request.client.host
    if current_user:
        # Check if this user already viewed this post
        existing_view = (
            db.query(View)
            .filter(View.post_id == post_id, View.user_id == current_user.id)
            .first()
        )
    else:
        # Check duplicate by IP for anonymous view
        existing_view = (
            db.query(View)
            .filter(View.post_id == post_id, View.ip_address == ip)
            .first()
        )

    if existing_view:
        return {"message": "View already recorded"}
    view = View(post_id=post_id, user_id=current_user.id if current_user else None, ip_address=ip)
    db.add(view)
    db.commit()
    return {"message": "View recorded"}

@router.get("/get-posts/{post_id}/views/")
async def get_views(post_id: int, db: Session = Depends(db_dependency)):
    views = db.query(View).filter(View.post_id == post_id).all()
    return {"post_id": post_id, "view_count": len(views)}
