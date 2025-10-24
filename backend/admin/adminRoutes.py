from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from database import get_db
from admin.adminModels import Admin
from admin.adminSchemas import AdminCreate, AdminUpdate, AdminResponse

router = APIRouter()

@router.get('/', response_model=List[AdminResponse])
async def list_admins(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Admin)
        )
    admins = result.scalars().all()
    return admins

