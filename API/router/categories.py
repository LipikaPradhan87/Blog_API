from .basic_import import *
from models.categories import Category
from slugify import slugify  # pip install python-slugify

router = APIRouter()


# ==============================
# Schemas
# ==============================
class CreateCategoryRequest(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# ==============================
# Create Category
# ==============================
@router.post("/create-category/")
async def create_category(
    category: CreateCategoryRequest,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    try:
        # Generate slug from name
        slug_value = slugify(category.name)

        # Check for duplicate slug or name
        existing = db.query(Category).filter(
            (Category.name == category.name) | (Category.slug == slug_value)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name or slug already exists")

        new_category = Category(
            name=category.name,
            slug=slug_value,
            description=category.description,
        )
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return {"message": "Category created successfully", "category": jsonable_encoder(new_category)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# Get All Categories
# ==============================
@router.get("/get-all-categories/")
async def get_all_categories(
    db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    categories = db.query(Category).all()
    return jsonable_encoder(categories)


# ==============================
# Get Category By ID
# ==============================
@router.get("/category-by-id/{category_id}")
async def get_category_by_id(
    category_id: int,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return jsonable_encoder(category)


# ==============================
# Update Category
# ==============================
@router.put("/update-category/{category_id}/")
async def update_category(
    category_id: int,
    request: UpdateCategoryRequest,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        # Update fields if provided
        if request.name:
            category.name = request.name
            category.slug = slugify(request.name)
        if request.description is not None:
            category.description = request.description

        db.commit()
        db.refresh(category)

        return {"message": "Category updated successfully", "category": jsonable_encoder(category)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# ==============================
# Delete Category
# ==============================
@router.delete("/delete-category/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        db.delete(category)
        db.commit()

        return {"message": "Category deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
