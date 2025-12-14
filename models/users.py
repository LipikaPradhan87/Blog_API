from . basic_import import *

class UserRole(enum.Enum):
    admin = "admin"
    author = "author"
    reader = "reader"
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    mobile = Column(String(20), nullable=False)
    profile_image = Column(Text, nullable=True) 
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole, name="user_roles"), nullable=False, default=UserRole.reader)
    created_at = Column(DateTime(timezone=False), default=func.now())
    updated_at = Column(DateTime(timezone=False), default=func.now(), onupdate=func.now())

    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    saved_posts = relationship("SavedPost", back_populates="user", cascade="all, delete-orphan")
    views = relationship("View", back_populates="user", cascade="all, delete-orphan")
