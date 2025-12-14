from .basic_import import *

class PostTag(Base):
    __tablename__ = "post_tags"
    __table_args__ = (UniqueConstraint('post_id', 'tag_id', name='unique_post_tag'),)

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    post = relationship("Post", back_populates="tags")
    tag = relationship("Tag", back_populates="posts")