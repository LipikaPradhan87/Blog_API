from .basic_import import *
from models.categories import Category
from typing import List, Optional
from fastapi import Body
import bcrypt
from pydantic import BaseModel


router = APIRouter()

class CreateCategoryRequest(BaseModel):
    name: str
    description: str
    image: Optional[str] = None

class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None

@router.post("/create-category/")
async def create_category(category: CreateCategoryRequest, db: Session = Depends(db_dependency)):
    try:
        new_categry = Category(
        name=category.name,
        description=category.description,
        image=category.image,
        )
        db.add(new_categry)
        db.commit()
        db.refresh(new_categry)    
        return {"message": "Category added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-all-categories/")
async def get_all_categories(db: Session = Depends(db_dependency)):
    data = db.query(Category).all()
    return jsonable_encoder(data)        
    
@router.get("/category-by-id/{category_id}")
async def get_category_by_id(category_id: int, db: Session = Depends(db_dependency)):
    categ = (
        db.query(Category).filter(Category.id == category_id).first())
    if not categ:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "id": categ.id,
        "name": categ.name,
        "description": categ.description,
        "image": categ.image,
    }

@router.delete("/delete-category/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(db_dependency)):
    try:
        categ = db.query(Category).filter(Category.id == category_id).first()
        if not categ:
            raise raise_exception(404, "Category Not Found!")
        db.delete(categ)
        db.commit()
        return succes_response(200, "Category deleted successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")


@router.put("/update-category/{category_id}/")
async def update_category(category_id: int, request: UpdateCategoryRequest, db: Session = Depends(db_dependency)):
    try:    
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        if request.image is not None and request.image != "string":
            category.image = request.image
        if request.image is not None and request.image != "string":
            category.image = request.image
        if request.image is not None and request.image != "string":
            category.image = request.image

        db.commit()
        db.refresh(category)

        return succes_response(category, "Category updated successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")