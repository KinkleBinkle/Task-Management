from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import ProjectRole, TaskStatus

### user schemas

class UserBase(BaseModel):
    name : str
    username : str
    email : EmailStr

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

### project schemas

class ProjectBase(BaseModel):
    name : str
    description : Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name : Optional[str] = None
    description : Optional[str] = None

class ProjectMemberInfo(BaseModel):
    id : int
    user_id : int
    username : str
    name : str
    role : ProjectRole

    class Config:
        from_attributes = True

class UserSimple(BaseModel):
    id : int
    username : str
    name : str

    class Config:
        from_attributes = True

class ProjectResponse(ProjectBase):
    id : int 
    owner_id : int
    owner : UserSimple
    created_at : datetime
    updated_at : datetime
    members : List[ProjectMemberInfo] = []

    class config:
        orm_mode = True
        from_attributes = True

class ProjectListResponse(BaseModel):
    id : int
    owner_id : int
    owner_name : str
    created_at : datetime
    task_count : Optional[int] = None
    member_count : Optional[int] = None

    class Config:

        from_attributes = True

### project member schemas

class ProjectMemberAdd(BaseModel):
    user_id : int
    role : ProjectRole = ProjectRole.MEMBER

class ProjectMemberUpdate(BaseModel):
    role : ProjectRole

class ProjectMemberResponse(BaseModel):
    id : int
    project_id : int
    user_id : int
    role : ProjectRole
    user : UserSimple
    joined_at : datetime

    class Config:
        orm_mode = True
        from_attributes = True

### task schemas

class TaskBase(BaseModel):
    title : str
    description : Optional[str] = None
    status : TaskStatus = TaskStatus.TODO
    assignee_id : Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title : Optional[str] = None
    description : Optional[str] = None
    status : Optional[TaskStatus] = None
    assignee_id : Optional[int] = None

class TaskResponse(TaskBase):
    id : int
    project_id : int
    created_at : datetime
    updated_at : datetime

    class Config:
        orm_mode = True
        from_attributes = True