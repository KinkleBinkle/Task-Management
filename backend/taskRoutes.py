from sqlalchemy.future import select, func
from FastAPI import APIRouter, depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload 
from database import get_db
from backend.models import user
from typing import List
from auth import get_current_user_with_db
from schemas import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse, ProjectMemberAdd, ProjectMemberResponse, ProjectMemberInfo

router = APIRouter()