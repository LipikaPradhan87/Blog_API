from .basic_import import *
from models.posts import Post
from models.tags import Tag
from models.post_tags import Post_tag
from router.notification import notify_new_post

router = APIRouter()

class CreatePostRequest(BaseModel):
    title: str
    content: str
    image: Optional[str] = None
    author_id: int
    category_id: int
    tag_names: List[str] = []  

class UpdatePostRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    author_id: Optional[int] = None
    category_id: Optional[int] = None    
    tag_names: List[str] = []  

@router.post("/create-post/")
async def create_post(post: CreatePostRequest, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    try:
        new_post = Post(
        title=post.title,
        content=post.content,
        image=post.image,
        author_id=post.author_id,
        category_id=post.category_id
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)    
        if post.tag_names:
            tag_objects = []
            for tag_name in post.tag_names:
                # Check if tag exists
                tag = db.query(Tag).filter(func.lower(Tag.name) == tag_name.lower()).first()
                if not tag:
                    # Create a new tag if not exists
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)
                tag_objects.append(tag)
            new_post.tags = tag_objects
            db.commit()
        notify_new_post(new_post, db)
        return {"message": "Post created successfully", "post_id": new_post.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-all-posts/")
async def get_all_posts(db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    posts = db.query(Post).all()
    result = []

    for post in posts:
        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "image": post.image,
            "author": post.author.username if post.author else None,
            "category": post.category.name if post.category else None,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "tags": [tag.name for tag in post.tags],
            "likes_count": len(post.likes),
            "comments_count": len(post.comments)
        })

    return result
     
    
@router.get("/posts-by-id/{post_id}")
async def get_post(post_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    post = (
        db.query(Post).filter(Post.id == post_id).first())
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "image": post.image,
        "author": post.author.username,
        "category": post.category.name if post.category else None,
        "tags": [tag.name for tag in post.tags],
        "likes_count": len(post.likes),
        "liked_users": [like.user.username for like in post.likes],
        "comments": [{"user": c.user.username, "content": c.content, "created_at": c.created_at} for c in post.comments],
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }
@router.delete("/delete-post/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise raise_exception(404, "Post Not Found!")
        db.delete(post)
        db.commit()
        return succes_response(200, "Post deleted successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")


@router.put("/update-post/{post_id}/")
async def update_post(post_id: int, request: UpdatePostRequest, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    try:    
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if request.title is not None and request.title != "string":
            post.title = request.title
        if request.content is not None and request.content != "string":
            post.content = request.content
        if request.image is not None and request.image != "string":
            post.image = request.image    
        if request.author_id is not None:
            post.author_id = request.author_id    
        if request.category_id is not None:
            post.category_id = request.category_id      

        if request.tag_names:
            tag_objects = []
            for tag_name in request.tag_names:
                # Check if tag exists
                tag = db.query(Tag).filter(func.lower(Tag.name) == tag_name.lower()).first()
                if not tag:
                    # Create a new tag if not exists
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)
                tag_objects.append(tag)
            post.tags = tag_objects
        db.commit()
        db.refresh(post)

        return succes_response(post, "Post updated successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")