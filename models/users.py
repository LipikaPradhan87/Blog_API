from . basic_import import *

class User(BASE):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    profile_image = Column(String(255), nullable=True)   # <-- new field
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="user")