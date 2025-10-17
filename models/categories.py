from .basic_import import *

class Category(BASE):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    image = Column(String(255), nullable=True)   # <-- new field

    posts = relationship("Post", back_populates="category")
