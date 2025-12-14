from .basic_import import *

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(150), unique=True, nullable=False)

    posts = relationship("PostTag", back_populates="tag", cascade="all, delete")
