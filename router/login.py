from .basic_import import *
from models.users import User, UserRole
from router.auth import create_access_token
from models.loginActivity import LoginActivity

router = APIRouter()


# ==============================
# Schemas
# ==============================
class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    mobile: str
    role: Optional[str] = "reader"
    bio: Optional[str] = None
    profile_image: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str


# ======================================
# Utilities
# ======================================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ======================================
# Signup
# ======================================
@router.post("/signup")
async def signup(user: SignUpRequest, db: Session = Depends(db_dependency)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_pw,
        mobile=user.mobile,
        profile_image=user.profile_image,
        bio=user.bio,
        role=UserRole[user.role] if user.role in UserRole.__members__ else UserRole.reader,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id)})

    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "mobile": new_user.mobile,
            "role": new_user.role.value,
            "bio": new_user.bio,
            "profile_image": new_user.profile_image,
        },
    }


# ======================================
# Login
# ======================================
@router.post("/login")
async def login(request_data: LoginRequest, request: Request, db: Session = Depends(db_dependency)):
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user or not verify_password(request_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    token = create_access_token({"sub": str(user.id)})
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    activity = LoginActivity(
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        login_time=datetime.utcnow()
    )
    db.add(activity)
    db.commit()
    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "mobile": user.mobile,
            "role": user.role.value,
            "bio": user.bio,
            "profile_image": user.profile_image,
        },
    }


# ======================================
# Password Reset
# ======================================
@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(db_dependency)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(request.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password reset successful"}