from .basic_import import *

class Notification(BASE):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Who will receive the notification
    actor_id = Column(Integer, ForeignKey("users.id")) # Who performed the action (author, liker, commenter)
    type = Column(String(50), nullable=False)  # 'post', 'like', 'comment'
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
    actor = relationship("User", foreign_keys=[actor_id])
    post = relationship("Post")
    comment = relationship("Comment")
