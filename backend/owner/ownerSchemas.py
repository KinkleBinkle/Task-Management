from pydantic import BaseModel
from typing import List, Optional

class OwnerBase(BaseModel):
    id: int
    name: str
    password: str
    username: str

class OwnerCreate(OwnerBase):
    pass

class OwnerUpdate(OwnerBase):
     password: Optional[str] = None
     name: Optional[str] = None

class OwnerResponse(OwnerBase):
    id: int
    username: str
    password: str
    class Config:
        orm_mode = True

