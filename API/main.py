from fastapi.middleware.cors import CORSMiddleware
from router import users,login, post, categories, tags, post_tags, comments, likes, notification, auth_routes, savedPost,views, loginActivity
from fastapi import FastAPI, Request
import os
from datetime import datetime, timedelta
import models  # this line imports all models and registers them with Base
from db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ThoughtNest",description="A nest for your thoughts")
origins = [
    "http://localhost:5173",  # The origin of your frontend application
    "http://localhost:3000",
    # "https://your-production-frontend.com",
    # You can add more specific origins here
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "Welcome to ThoughtNest API"}

app.include_router(
    auth_routes.router,
    prefix="/Auth",
    tags=["Auth"]
)
app.include_router(
    users.router,
    prefix="/Users",
    tags=["Users"]
)
app.include_router(
    login.router,
    prefix="/Login",
    tags=["Login"]
)
app.include_router(
    categories.router,
    prefix="/Category",
    tags=["Category"]
)

app.include_router(
    tags.router,
    prefix="/Tag",
    tags=["Tag"]
)
app.include_router(
    post.router,
    prefix="/Post",
    tags=["Post"]
)
app.include_router(
    post_tags.router,
    prefix="/Post_tag",
    tags=["Post_tag"]
)
app.include_router(
    comments.router,
    prefix="/Comments",
    tags=["Comments"]
)
app.include_router(
    likes.router,
    prefix="/PostLikes",
    tags=["PostLikes"]
)
app.include_router(
    notification.router,
    prefix="/Notification",
    tags=["Notification"]
)
app.include_router(
    savedPost.router,
    prefix="/SavedPost",
    tags=["SavedPost"]
)
app.include_router(
    views.router,
    prefix="/Views",
    tags=["Views"]
)
app.include_router(
    loginActivity.router,
    prefix="/LoginActivity",
    tags=["LoginActivity"]
)