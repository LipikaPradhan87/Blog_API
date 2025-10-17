from .basic_import import *
from models.users import User
from typing import Optional
from fastapi import Depends, HTTPException
import bcrypt
from pydantic import BaseModel

router = APIRouter()


# ==============================
# Schemas
# ==============================
class SignUpRequest(BaseModel):
    username: str
    email: str
    password: str
    profile_image: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str


# ==============================
# Utility: Password Hashing
# ==============================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# ==============================
# Sign Up API
# ==============================
@router.post("/signup")
async def signup(user: SignUpRequest, db: Session = Depends(db_dependency)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(user.password)

    # Create user
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw,
        profile_image=user.profile_image
    )
    print(new_user,"lll")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}


# ==============================
# Login API
# ==============================
@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(db_dependency)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "user_id": user.id}


# ==============================
# Reset Password API
# ==============================
@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(db_dependency)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(request.new_password)
    db.commit()
    db.refresh(user)

    return {"message": "Password reset successful"}
