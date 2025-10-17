from .basic_import import *

class Tag(BASE):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    posts = relationship("Post", secondary="post_tags", back_populates="tags")
