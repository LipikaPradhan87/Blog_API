from fastapi.middleware.cors import CORSMiddleware
from router import users,login, post, categories, tags, post_tags, comments, likes, notification
from fastapi import FastAPI, Request
import os
from datetime import datetime, timedelta

app = FastAPI(title="ThoughtNest",description="A nest for your thoughts")

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