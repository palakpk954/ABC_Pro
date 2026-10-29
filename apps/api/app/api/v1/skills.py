from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_org_id
from app.models import Skill, User
from app.schemas.skill import SkillCreate, SkillUpdate, SkillResponse
from app.services.audit import log_audit_event

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("", response_model=List[SkillResponse])
def list_skills(
    db: Session = Depends(get_db),
    org_id: str = Depends(get_current_org_id),
):
    return db.query(Skill).filter(Skill.org_id == org_id).all()


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_in: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Skill).filter(
        Skill.org_id == current_user.org_id,
        Skill.name == skill_in.name,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill with this name already exists in organization")

    skill = Skill(
        org_id=current_user.org_id,
        name=skill_in.name,
        category=skill_in.category,
        description=skill_in.description,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="create",
        entity_type="skill",
        entity_id=skill.id,
        after_state={"name": skill.name, "category": skill.category},
    )
    db.commit()

    return skill


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: str,
    db: Session = Depends(get_db),
    org_id: str = Depends(get_current_org_id),
):
    skill = db.query(Skill).filter(Skill.id == skill_id, Skill.org_id == org_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: str,
    skill_in: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skill = db.query(Skill).filter(Skill.id == skill_id, Skill.org_id == current_user.org_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    before_state = {"name": skill.name, "category": skill.category}

    if skill_in.name is not None:
        skill.name = skill_in.name
    if skill_in.category is not None:
        skill.category = skill_in.category
    if skill_in.description is not None:
        skill.description = skill_in.description

    db.commit()
    db.refresh(skill)

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="update",
        entity_type="skill",
        entity_id=skill.id,
        before_state=before_state,
        after_state={"name": skill.name, "category": skill.category},
    )
    db.commit()

    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skill = db.query(Skill).filter(Skill.id == skill_id, Skill.org_id == current_user.org_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(skill)
    db.commit()

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="delete",
        entity_type="skill",
        entity_id=skill_id,
        before_state={"name": skill.name},
    )
    db.commit()
