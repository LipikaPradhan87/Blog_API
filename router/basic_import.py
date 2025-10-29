from db import db_dependency,engine
from fastapi import Depends
from typing import List, Optional
from fastapi import Body
from sqlalchemy.orm import Session, joinedload
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter,status
from pydantic import BaseModel,Field,EmailStr,validator
from datetime import datetime
import bcrypt
import re,json
from sqlalchemy import func
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os
from models.users import User
from .auth import get_current_user

def raise_exception(error_code:int=None,msg:str=None):
    raise HTTPException(status_code=error_code,detail=jsonable_encoder(msg))

def succes_response(data=None,msg=None):
    return {"status_code":200,"msg":msg,"response":jsonable_encoder(data)}