import select
from FastAPI import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session, get_db
from backend.models import user
from typing import List
from auth import get_password_hash, verify_password, create_access_token, get_current_user_with_db
from schemas import UserCreate, UserResponse

router = APIRouter()
router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)

async def register_user(user_data: UserCreate, db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(user).where(user.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    new_user = user(username=user_data.username, name=user_data.name, password=get_password_hash(user_data.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
