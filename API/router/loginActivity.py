from .basic_import import *
from models.loginActivity import LoginActivity

router = APIRouter()

@router.get("/login-activity/{user_id}")
def get_login_activity(user_id: int, db: Session = Depends(db_dependency), current_user: User = Depends(get_current_user)):
    activities = db.query(LoginActivity).filter(LoginActivity.user_id == user_id).order_by(LoginActivity.login_time.desc()).all()
    return {"data": [
        {"ip_address": a.ip_address, "user_agent": a.user_agent, "login_time": a.login_time} 
        for a in activities
    ]}
