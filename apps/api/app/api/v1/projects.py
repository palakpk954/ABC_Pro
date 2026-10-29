from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_org_id
from app.models import Project, ProjectRole, ProjectRoleSkill, Skill, User
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectRoleCreate,
    ProjectRoleUpdate,
    ProjectRoleResponse,
    ProjectRoleSkillResponse,
)
from app.services.audit import log_audit_event

router = APIRouter(prefix="/projects", tags=["Projects"])


def format_project_response(p: Project) -> ProjectResponse:
    roles_resp = []
    for r in p.roles:
        skills_resp = [
            ProjectRoleSkillResponse(
                id=prs.id,
                project_role_id=prs.project_role_id,
                skill_id=prs.skill_id,
                skill_name=prs.skill.name if prs.skill else None,
                min_proficiency=prs.min_proficiency,
            )
            for prs in r.skill_requirements
        ]
        roles_resp.append(
            ProjectRoleResponse(
                id=r.id,
                project_id=r.project_id,
                role_title=r.role_title,
                hours_per_week=r.hours_per_week,
                start_date=r.start_date,
                end_date=r.end_date,
                is_stretch_allowed=r.is_stretch_allowed,
                skill_requirements=skills_resp,
            )
        )

    return ProjectResponse(
        id=p.id,
        org_id=p.org_id,
        name=p.name,
        client=p.client,
        start_date=p.start_date,
        end_date=p.end_date,
        revenue=p.revenue,
        billing_rate_hourly=p.billing_rate_hourly,
        priority=p.priority,
        mandatory=p.mandatory,
        status=p.status,
        roles=roles_resp,
    )


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    org_id: str = Depends(get_current_org_id),
):
    projects = db.query(Project).filter(Project.org_id == org_id).all()
    return [format_project_response(p) for p in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    proj_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if proj_in.start_date > proj_in.end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    proj = Project(
        org_id=current_user.org_id,
        name=proj_in.name,
        client=proj_in.client,
        start_date=proj_in.start_date,
        end_date=proj_in.end_date,
        revenue=proj_in.revenue,
        billing_rate_hourly=proj_in.billing_rate_hourly,
        priority=proj_in.priority,
        mandatory=proj_in.mandatory,
        status=proj_in.status,
    )
    db.add(proj)
    db.flush()

    for r_in in proj_in.roles:
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

        for s_in in r_in.skills:
            prs = ProjectRoleSkill(
                org_id=current_user.org_id,
                project_role_id=role.id,
                skill_id=s_in.skill_id,
                min_proficiency=s_in.min_proficiency,
            )
            db.add(prs)

    db.commit()
    db.refresh(proj)

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="create",
        entity_type="project",
        entity_id=proj.id,
        after_state={"name": proj.name, "client": proj.client, "revenue": proj.revenue, "mandatory": proj.mandatory},
    )
    db.commit()

    return format_project_response(proj)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    org_id: str = Depends(get_current_org_id),
):
    p = db.query(Project).filter(Project.id == project_id, Project.org_id == org_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return format_project_response(p)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    proj_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = db.query(Project).filter(Project.id == project_id, Project.org_id == current_user.org_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    before_state = {"name": p.name, "revenue": p.revenue, "mandatory": p.mandatory}

    if proj_in.name is not None:
        p.name = proj_in.name
    if proj_in.client is not None:
        p.client = proj_in.client
    if proj_in.start_date is not None:
        p.start_date = proj_in.start_date
    if proj_in.end_date is not None:
        p.end_date = proj_in.end_date
    if proj_in.revenue is not None:
        p.revenue = proj_in.revenue
    if proj_in.billing_rate_hourly is not None:
        p.billing_rate_hourly = proj_in.billing_rate_hourly
    if proj_in.priority is not None:
        p.priority = proj_in.priority
    if proj_in.mandatory is not None:
        p.mandatory = proj_in.mandatory
    if proj_in.status is not None:
        p.status = proj_in.status

    db.commit()
    db.refresh(p)

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="update",
        entity_type="project",
        entity_id=p.id,
        before_state=before_state,
        after_state={"name": p.name, "revenue": p.revenue, "mandatory": p.mandatory},
    )
    db.commit()

    return format_project_response(p)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = db.query(Project).filter(Project.id == project_id, Project.org_id == current_user.org_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(p)
    db.commit()

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="delete",
        entity_type="project",
        entity_id=project_id,
        before_state={"name": p.name},
    )
    db.commit()


# Project Roles Sub-endpoints
@router.post("/{project_id}/roles", response_model=ProjectRoleResponse, status_code=status.HTTP_201_CREATED)
def create_project_role(
    project_id: str,
    role_in: ProjectRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = db.query(Project).filter(Project.id == project_id, Project.org_id == current_user.org_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    role = ProjectRole(
        org_id=current_user.org_id,
        project_id=project_id,
        role_title=role_in.role_title,
        hours_per_week=role_in.hours_per_week,
        start_date=role_in.start_date,
        end_date=role_in.end_date,
        is_stretch_allowed=role_in.is_stretch_allowed,
    )
    db.add(role)
    db.flush()

    for s_in in role_in.skills:
        prs = ProjectRoleSkill(
            org_id=current_user.org_id,
            project_role_id=role.id,
            skill_id=s_in.skill_id,
            min_proficiency=s_in.min_proficiency,
        )
        db.add(prs)

    db.commit()
    db.refresh(role)

    skills_resp = [
        ProjectRoleSkillResponse(
            id=prs.id,
            project_role_id=prs.project_role_id,
            skill_id=prs.skill_id,
            skill_name=prs.skill.name if prs.skill else None,
            min_proficiency=prs.min_proficiency,
        )
        for prs in role.skill_requirements
    ]
    return ProjectRoleResponse(
        id=role.id,
        project_id=role.project_id,
        role_title=role.role_title,
        hours_per_week=role.hours_per_week,
        start_date=role.start_date,
        end_date=role.end_date,
        is_stretch_allowed=role.is_stretch_allowed,
        skill_requirements=skills_resp,
    )
