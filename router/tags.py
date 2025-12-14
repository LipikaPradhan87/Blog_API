from .basic_import import *
from models.tags import Tag
from models.post_tags import PostTag
from models.posts import Post
from slugify import slugify

router = APIRouter()

class CreateTagRequest(BaseModel):
    name: str

@router.post("/create-tags/")
async def create_tag(request: CreateTagRequest, db: Session = Depends(db_dependency)):
    slug = slugify(request.name)
    existing = db.query(Tag).filter(Tag.slug == slug).first()
    if existing:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    tag = Tag(name=request.name, slug=slug)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return {"message": "Tag created successfully", "tag": jsonable_encoder(tag)}

@router.get("/tags/")
async def get_tags(db: Session = Depends(db_dependency)):
    tags = db.query(Tag).all()
    return jsonable_encoder(tags)

@router.post("/add-tag-to-posts/{post_id}/tags/{tag_id}/")
async def add_tag_to_post(post_id: int, tag_id: int, db: Session = Depends(db_dependency)):
    post = db.query(Post).filter(Post.id == post_id).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not post or not tag:
        raise HTTPException(status_code=404, detail="Post or Tag not found")

    existing = db.query(PostTag).filter_by(post_id=post_id, tag_id=tag_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already added to post")

    post_tag = PostTag(post_id=post_id, tag_id=tag_id)
    db.add(post_tag)
    db.commit()
    return {"message": "Tag added to post successfully"}

@router.delete("/delete-posts/{post_id}/tags/{tag_id}/")
async def remove_tag_from_post(post_id: int, tag_id: int, db: Session = Depends(db_dependency)):
    post_tag = db.query(PostTag).filter_by(post_id=post_id, tag_id=tag_id).first()
    if not post_tag:
        raise HTTPException(status_code=404, detail="Tag not found on post")

    db.delete(post_tag)
    db.commit()
    return {"message": "Tag removed from post"}
