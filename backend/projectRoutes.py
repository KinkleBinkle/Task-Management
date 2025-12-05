from sqlalchemy import select, func
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload 
from database import get_db
from models import Project, ProjectMember, User
from typing import List, Optional
from auth import get_current_user_with_db
from schemas import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse, ProjectMemberAdd, ProjectMemberResponse, ProjectMemberUpdate

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
async def list_projects(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_with_db)):
    # Get projects where user is owner
    owned_projects_result = await db.execute(
        select(Project).where(Project.owner_id == current_user.id)
    )
    owned_projects = owned_projects_result.scalars().all()
    
    # Get projects where user is a member
    member_projects_result = await db.execute(
        select(Project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == current_user.id)
    )
    member_projects = member_projects_result.scalars().all()
    
    # Combine and deduplicate
    all_projects = {p.id: p for p in owned_projects}
    for p in member_projects:
        if p.id not in all_projects:
            all_projects[p.id] = p
    
    response = []
    for project in all_projects.values():
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
    
    # Check if user is owner or member
    is_owner = project.owner_id == current_user.id
    is_member = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        )
    )
    member_exists = is_member.scalar_one_or_none()
    
    if not is_owner and not member_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this project")
    
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

### Project Member Management

@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def get_project_members(project_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_with_db)):
    # Check if project exists
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Check if user is owner or member
    is_owner = project.owner_id == current_user.id
    is_member = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        )
    )
    member_exists = is_member.scalar_one_or_none()
    
    if not is_owner and not member_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only project members can view member list")
    
    # Get all members with user details
    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.project_id == project_id)
    )
    members = result.scalars().all()
    return members

@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_project_member(project_id: int, member_data: ProjectMemberAdd, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_with_db)):
    # Check if project exists
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Only owner can add members
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only project owner can add members")
    
    # Check if user exists
    user_result = await db.execute(select(User).where(User.id == member_data.user_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if already a member
    existing_member = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_data.user_id
        )
    )
    if existing_member.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member")
    
    # Add member
    new_member = ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role=member_data.role
    )
    db.add(new_member)
    await db.commit()
    
    # Refresh and return with user details
    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.id == new_member.id)
    )
    return result.scalar_one()

@router.put("/{project_id}/members/{member_id}", response_model=ProjectMemberResponse)
async def update_project_member(project_id: int, member_id: int, member_data: ProjectMemberUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_with_db)):
    # Check if project exists
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Only owner can update member roles
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only project owner can update member roles")
    
    # Get member
    member_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id == member_id,
            ProjectMember.project_id == project_id
        )
    )
    member = member_result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    
    # Update role
    member.role = member_data.role
    await db.commit()
    
    # Refresh and return with user details
    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.id == member_id)
    )
    return result.scalar_one()

@router.delete("/{project_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(project_id: int, member_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_with_db)):
    # Check if project exists
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Only owner can remove members
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only project owner can remove members")
    
    # Get member
    member_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id == member_id,
            ProjectMember.project_id == project_id
        )
    )
    member = member_result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    
    # Remove member
    await db.delete(member)
    await db.commit()


