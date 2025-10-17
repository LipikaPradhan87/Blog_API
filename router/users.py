from .basic_import import *
from models.users import User
from typing import List, Optional
from fastapi import Body
import bcrypt
from pydantic import BaseModel


router = APIRouter()

class UserBase(BaseModel):
    username: str
    email: str
    password_hash: str
    profile_image: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime


class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: Optional[bool] = None

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()  # Generate a salt for the hashing
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hash the password with salt
    return hashed.decode('utf-8') 
    
@router.post("/create-user/")
async def create_user(user: UserBase, db: Session = Depends(db_dependency)):
    try:
        user.password_hash = hash_password(user.password_hash)
        data = User(
            username = user.username,
            email = user.email,
            password_hash = user.password_hash,
            profile_image = user.profile_image,
            is_active = user.is_active,
            created_at = user.created_at
        )
        db.add(data)
        db.commit()
        db.refresh(data)
        return succes_response(data, "User added successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")
    

@router.get("/get-users/")
async def get_users(db: Session = Depends(db_dependency)):
    data = db.query(User).filter(User.is_active == True).all()
    return jsonable_encoder(data)    

@router.get("/get-users-by-id/")
async def get_users_by_id(user_id: int, db: Session = Depends(db_dependency)):
    data = db.query(User).filter(User.id == user_id).first()
    return jsonable_encoder(data)  

@router.delete("/delete-user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(db_dependency)):
    try:
        userData = db.query(User).filter(User.id == user_id).first()
        if not userData:
            raise raise_exception(404, "User Not Found!")
        userData.is_active = False
        db.commit()
        db.refresh(userData)
        return succes_response(200, "User deleted successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")
    
@router.put("/update-user/{user_id}")
async def update_user(user_id: int, request: UpdateUserRequest, db: Session = Depends(db_dependency)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update fields if provided
        if request.username is not None:
            user.username = request.username
        if request.email is not None:
            # check if new email already exists for another user
            existing_email = db.query(User).filter(User.email == request.email, User.id != user_id).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already registered with another user")
            user.email = request.email
        if request.password is not None and request.password.strip() != "" and request.password.lower() != "string":
            user.password_hash = hash_password(request.password)
        if request.profile_image is not None and request.profile_image != "string":
            user.profile_image = request.profile_image
        if request.is_active is not None:
            user.is_active = request.is_active
    
        db.commit()
        db.refresh(user)

        return succes_response(user, "User updated successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")