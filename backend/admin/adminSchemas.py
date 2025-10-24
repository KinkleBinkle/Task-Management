from pydantic import BaseModel
from typing import List, Optional

class AdminBase(BaseModel):
    id: int
    name: str
    password: str
    username: str

class AdminCreate(AdminBase):
    pass

class AdminUpdate(AdminBase):
     password: Optional[str] = None
     name: Optional[str] = None

class AdminResponse(AdminBase):
    id: int
    username: str
    password: str
    class Config:
        orm_mode = True

