from .basic_import import *
from models.users import User, UserRole


router = APIRouter()


class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str
    mobile: str
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[str] = Field(default="reader")
    is_active: bool = True


class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    mobile: Optional[str] = None
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# ==========================
# Utility Functions
# ==========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# ==========================
# Create User
# ==========================
@router.post("/create-user/")
async def create_user(user: UserBase, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    try:
        # Check for duplicate email
        existing = db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered.")

        new_user = User(
            username=user.username,
            email=user.email,
            password=hash_password(user.password),
            mobile=user.mobile,
            profile_image=user.profile_image,
            bio=user.bio,
            role=UserRole[user.role] if user.role in UserRole.__members__ else UserRole.reader,
            is_active=user.is_active,
            created_at=datetime.utcnow(),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return succes_response(new_user, "User created successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")


# ==========================
# Get All Active Users
# ==========================
@router.get("/get-users/")
async def get_users(db: Session = Depends(db_dependency)):
    users = db.query(User).filter(User.is_active == True).all()
    return jsonable_encoder(users)


# ==========================
# Get User by ID
# ==========================
@router.get("/get-user/{user_id}")
async def get_user_by_id(user_id: int, db: Session = Depends(db_dependency)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return jsonable_encoder(user)


# ==========================
# Update User
# ==========================
@router.put("/update-user/{user_id}")
async def update_user(user_id: int, request: UpdateUserRequest, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if request.username:
            user.username = request.username
        if request.email:
            existing = db.query(User).filter(User.email == request.email, User.id != user_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already in use.")
            user.email = request.email
        if request.password:
            user.password = hash_password(request.password)
        if request.mobile:
            user.mobile = request.mobile    
        if request.profile_image:
            user.profile_image = request.profile_image
        if request.bio:
            user.bio = request.bio
        if request.role and request.role in UserRole.__members__:
            user.role = UserRole[request.role]
        if request.is_active is not None:
            user.is_active = request.is_active

        db.commit()
        db.refresh(user)
        return succes_response(user, "User updated successfully.")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")


# ==========================
# Delete (Soft Delete) User
# ==========================
@router.delete("/delete-user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
    return succes_response(200, "User deactivated successfully.")


@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    # Verify old password
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    # Hash new password
    hashed = hash_password(data.new_password)
    current_user.password = hashed

    db.commit()
    db.refresh(current_user)

    return {"message": "Password changed successfully"}
