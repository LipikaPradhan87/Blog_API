from .basic_import import *
from models.tags import Tag
from typing import List, Optional
from fastapi import Body
import bcrypt
from pydantic import BaseModel


router = APIRouter()

class PostTagRequest(BaseModel):
    name: str

@router.post("/create-tag/")
async def create_tag(tags: PostTagRequest, db: Session = Depends(db_dependency)):
    try:
        new_tag = Tag(
        name=tags.name,
        )
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)    
        return {"message": "Tag created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-all-tags/")
async def get_all_tags(db: Session = Depends(db_dependency)):
    data = db.query(Tag).all()
    return jsonable_encoder(data)        
    
@router.get("/tag-by-id/{tag_id}")
async def get_tag_by_id(tag_id: int, db: Session = Depends(db_dependency)):
    tag = (
        db.query(Tag).filter(Tag.id == tag_id).first())
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return {
        "id": tag.id,
        "name": tag.name,
    }

@router.delete("/delete-tag/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(db_dependency)):
    try:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise raise_exception(404, "Tag Not Found!")
        db.delete(tag)
        db.commit()
        return succes_response(200, "Tag deleted successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")


@router.put("/update-tag/{tag_id}/")
async def update_tag(tag_id: int, request: PostTagRequest, db: Session = Depends(db_dependency)):
    try:    
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        if request.name is not None and request.name != "string":
            tag.name = request.name

        db.commit()
        db.refresh(tag)

        return succes_response(tag, "Tag updated successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")
    
