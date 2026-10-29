from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.skill import Skill
from app.models.user import User
from app.schemas.skill import SkillCreate, SkillResponse, SkillUpdate

router = APIRouter()


@router.get("", response_model=List[SkillResponse])
def list_skills(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all skills scoped to tenant."""
    query = db.query(Skill).filter(Skill.org_id == current_user.org_id)
    if category:
        query = query.filter(Skill.category == category)
    return query.order_by(Skill.name).all()


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    req: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new skill in the catalog."""
    existing = (
        db.query(Skill)
        .filter(Skill.org_id == current_user.org_id, Skill.name == req.name)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill '{req.name}' already exists in your organization",
        )

    skill = Skill(
        org_id=current_user.org_id,
        name=req.name,
        category=req.category,
        description=req.description,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skill = (
        db.query(Skill)
        .filter(Skill.id == skill_id, Skill.org_id == current_user.org_id)
        .first()
    )
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: str,
    req: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skill = (
        db.query(Skill)
        .filter(Skill.id == skill_id, Skill.org_id == current_user.org_id)
        .first()
    )
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    if req.name is not None:
        skill.name = req.name
    if req.category is not None:
        skill.category = req.category
    if req.description is not None:
        skill.description = req.description

    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skill = (
        db.query(Skill)
        .filter(Skill.id == skill_id, Skill.org_id == current_user.org_id)
        .first()
    )
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
