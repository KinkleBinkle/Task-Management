from sqlalchemy import select, func
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload 
from database import get_db
from models import Project, ProjectMember, User
from typing import List, Optional
from auth import get_current_user_with_db
from schemas import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_with_db)):
    new_project = Project(owner_id=current_user.id, name=project_data.name, description=project_data.description)
    db.add(new_project)
    await db.commit()
    result = await db.execute(
        select(Project).options(selectinload(Project.owner), selectinload(Project.members)).where(Project.id == new_project.id)
    )
    project = result.scalar_one()
    await db.refresh(new_project)
    return project

@router.get("/", response_model=List[ProjectListResponse])
async def list_projects(db: AsyncSession = Depends(get_db), user_id: Optional[int] = None):
    query = select(Project)
    if user_id:
        query = query.join(ProjectMember).where(ProjectMember.user_id == user_id)
    result = await db.execute(query)
    projects = result.scalars().all()
    response = []
    for project in projects:
        owner_result = await db.execute(select(User).where(User.id == project.owner_id))
        owner = owner_result.scalar_one()
        count_members_result = await db.execute(select(func.count(ProjectMember.id)).where(ProjectMember.project_id == project.id))
        response.append(ProjectListResponse(
            id=project.id,
            owner_id=project.owner_id,
            owner_name=owner.name,
            created_at=project.created_at if hasattr(project, 'created_at') else None,
            member_count=count_members_result.scalar() or 0,
            task_count=0
        ))
    return response

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_with_db)):
    result = await db.execute(
        select(Project).options(selectinload(Project.owner), selectinload(Project.members)).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project_data: ProjectUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_with_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this project")
    
    update_data = project_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    await db.commit()
    await db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_with_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this project")
    
    await db.delete(project)
    await db.commit()

