from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.project import Project, ProjectRole, ProjectRoleSkill
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectRoleCreate,
    ProjectRoleResponse,
    ProjectUpdate,
)

router = APIRouter()


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    status: Optional[str] = Query(None),
    client: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List projects in organization with their roles and skill demands."""
    query = (
        db.query(Project)
        .options(
            joinedload(Project.roles)
            .joinedload(ProjectRole.skill_requirements)
            .joinedload(ProjectRoleSkill.skill)
        )
        .filter(Project.org_id == current_user.org_id)
    )
    if status:
        query = query.filter(Project.status == status)
    if client:
        query = query.filter(Project.client == client)
    if search:
        query = query.filter(
            Project.name.ilike(f"%{search}%") | Project.client.ilike(f"%{search}%")
        )
    return query.order_by(Project.start_date).all()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    req: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new candidate or active project."""
    proj = Project(
        org_id=current_user.org_id,
        name=req.name,
        client=req.client,
        start_date=req.start_date,
        end_date=req.end_date,
        revenue=req.revenue,
        billing_rate_hourly=req.billing_rate_hourly,
        priority=req.priority,
        mandatory=req.mandatory,
        status=req.status,
    )
    db.add(proj)
    db.flush()

    if req.roles:
        for r_in in req.roles:
            role = ProjectRole(
                org_id=current_user.org_id,
                project_id=proj.id,
                role_title=r_in.role_title,
                hours_per_week=r_in.hours_per_week,
                start_date=r_in.start_date,
                end_date=r_in.end_date,
                is_stretch_allowed=r_in.is_stretch_allowed,
            )
            db.add(role)
            db.flush()

            if r_in.skill_requirements:
                for sr_in in r_in.skill_requirements:
                    rs = ProjectRoleSkill(
                        org_id=current_user.org_id,
                        project_role_id=role.id,
                        skill_id=sr_in.skill_id,
                        min_proficiency=sr_in.min_proficiency,
                    )
                    db.add(rs)

    db.commit()
    db.refresh(proj)
    return proj


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proj = (
        db.query(Project)
        .options(
            joinedload(Project.roles)
            .joinedload(ProjectRole.skill_requirements)
            .joinedload(ProjectRoleSkill.skill)
        )
        .filter(Project.id == project_id, Project.org_id == current_user.org_id)
        .first()
    )
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    req: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proj = (
        db.query(Project)
        .filter(Project.id == project_id, Project.org_id == current_user.org_id)
        .first()
    )
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(proj, field, val)

    db.commit()
    db.refresh(proj)
    return proj


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proj = (
        db.query(Project)
        .filter(Project.id == project_id, Project.org_id == current_user.org_id)
        .first()
    )
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(proj)
    db.commit()


@router.post("/{project_id}/roles", response_model=ProjectRoleResponse, status_code=status.HTTP_201_CREATED)
def add_project_role(
    project_id: str,
    req: ProjectRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a staffing demand role to a project."""
    proj = (
        db.query(Project)
        .filter(Project.id == project_id, Project.org_id == current_user.org_id)
        .first()
    )
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    role = ProjectRole(
        org_id=current_user.org_id,
        project_id=project_id,
        role_title=req.role_title,
        hours_per_week=req.hours_per_week,
        start_date=req.start_date,
        end_date=req.end_date,
        is_stretch_allowed=req.is_stretch_allowed,
    )
    db.add(role)
    db.flush()

    if req.skill_requirements:
        for sr in req.skill_requirements:
            rs = ProjectRoleSkill(
                org_id=current_user.org_id,
                project_role_id=role.id,
                skill_id=sr.skill_id,
                min_proficiency=sr.min_proficiency,
            )
            db.add(rs)

    db.commit()
    db.refresh(role)
    return role


@router.delete("/{project_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_role(
    project_id: str,
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = (
        db.query(ProjectRole)
        .filter(
            ProjectRole.id == role_id,
            ProjectRole.project_id == project_id,
            ProjectRole.org_id == current_user.org_id,
        )
        .first()
    )
    if not role:
        raise HTTPException(status_code=404, detail="Project role not found")
    db.delete(role)
    db.commit()
