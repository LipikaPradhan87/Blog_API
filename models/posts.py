from .basic_import import *
class Post(BASE):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    image = Column(String(255), nullable=True)   # <-- new field
    author_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("PostLike", back_populates="post")
    tags = relationship("Tag", secondary="post_tags", back_populates="posts")
    category = relationship("Category", back_populates="posts")
