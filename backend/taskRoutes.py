from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Task, user
from typing import List
from auth import get_current_user_with_db
from schemas import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()

@router.post("/{project_id}/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(project_id: int, task_data: TaskCreate, db: AsyncSession = Depends(get_db), current_user: user = Depends(get_current_user_with_db)):
    new_task = Task(
        project_id=project_id,
        title=task_data.title,
        description=task_data.description,
        assignee_id=task_data.assignee_id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@router.get("/{project_id}/tasks/", response_model=List[TaskResponse])
async def get_project_tasks(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.project_id == project_id))
    tasks = result.scalars().all()
    return tasks

@router.put("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(project_id: int, task_id: int, task_data: TaskUpdate, db: AsyncSession = Depends(get_db), current_user: user = Depends(get_current_user_with_db)):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.project_id == project_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(project_id: int, task_id: int, db: AsyncSession = Depends(get_db), current_user: user = Depends(get_current_user_with_db)):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.project_id == project_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
