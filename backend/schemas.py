from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import ProjectRole, TaskStatus

### user schemas

class UserBase(BaseModel):
    name : str
    username : str

class UserCreate(UserBase):
    password : str

class UserUpdate(BaseModel):
    name : Optional[str] = None
    password : Optional[str] = None

class UserResponse(UserBase):
    id : int

    class Config:
        orm_mode = True
        from_attributes = True

class UserLogin(BaseModel):
    username : str
    password : str
