from .basic_import import *
from .auth import create_access_token
from models.users import User


router = APIRouter()

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_dependency)):
    user = db.query(User).filter(User.email == form_data.username).first()
    print(user)
    if not user or not bcrypt.checkpw(form_data.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": str(user.id)}, expires_minutes=60
    )
    return {"access_token": token, "token_type": "bearer"}
