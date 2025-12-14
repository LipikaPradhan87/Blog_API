from .basic_import import *

class View(Base):
    __tablename__ = "views"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="NO ACTION"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="NO ACTION"), nullable=True)
    ip_address = Column(String(100))
    viewed_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="views")
    user = relationship("User", back_populates="views")
