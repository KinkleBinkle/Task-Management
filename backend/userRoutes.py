from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import user
from typing import List
from auth import get_password_hash, verify_password, create_access_token, get_current_user_with_db
from schemas import UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(user).where(user.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    new_user = user(username=user_data.username, name=user_data.name, password=get_password_hash(user_data.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login_user(user_data: UserCreate, db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(user).where(user.username == user_data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user is None or not verify_password(user_data.password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(existing_user.id)})
    return {"access_token": access_token, "token_type": "bearer", "user_id": existing_user.id, "username": existing_user.username}

@router.post("/me", response_model=UserResponse)
async def get_current_user_with_info(current_user: user = Depends(get_current_user_with_db), db: AsyncSession = Depends(get_db)):
    return current_user

@router.get("/", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(user))
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(user).where(user.id == user_id))
    user_obj = result.scalar_one_or_none()
    if user_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_obj

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserCreate, db: AsyncSession = Depends(get_db), current_user: user = Depends(get_current_user_with_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
    
    result = await db.execute(select(user).where(user.id == user_id))
    user_obj = result.scalar_one_or_none()
    if user_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = user_data.model_dump(exclude_unset=True)

    if "username" in update_data:
        existing_user_result = await db.execute(select(user).where(user.username == user_data.username, user.id != user_id))
        if existing_user_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        
    for key, value in update_data.items():
        if key == "password":
            setattr(user_obj, key, get_password_hash(value))
        else:
            setattr(user_obj, key, value)

    await db.commit()
    await db.refresh(user_obj)
    return user_obj

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: user = Depends(get_current_user_with_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
    
    result = await db.execute(select(user).where(user.id == user_id))
    user_obj = result.scalar_one_or_none()
    if user_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await db.delete(user_obj)
    await db.commit()
    return None



