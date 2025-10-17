from .basic_import import *

class PostLike(BASE):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", backref="likes")
    user = relationship("User", backref="likes")
    post = relationship("Post", back_populates="likes")
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uix_post_user"),)
