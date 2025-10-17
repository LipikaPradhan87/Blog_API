from db import db_dependency,engine
from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter,status
from pydantic import BaseModel,Field,EmailStr,validator
from fastapi.exceptions import HTTPException
from datetime import datetime
import re,json
from enum import Enum
from sqlalchemy import func


def raise_exception(error_code:int=None,msg:str=None):
    raise HTTPException(status_code=error_code,detail=jsonable_encoder(msg))

def succes_response(data=None,msg=None):
    return {"status_code":200,"msg":msg,"response":jsonable_encoder(data)}