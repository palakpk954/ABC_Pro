from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.employee import Employee, EmployeeLeave
from app.models.skill import EmployeeSkill, Skill
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeLeaveCreate,
    EmployeeLeaveResponse,
    EmployeeResponse,
    EmployeeSkillCreate,
    EmployeeSkillResponse,
    EmployeeUpdate,
)

router = APIRouter()


@router.get("", response_model=List[EmployeeResponse])
def list_employees(
    is_active: Optional[bool] = Query(None),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List employees in organization with their skills and leaves."""
    query = (
        db.query(Employee)
        .options(
            joinedload(Employee.skills).joinedload(EmployeeSkill.skill),
            joinedload(Employee.leaves),
        )
        .filter(Employee.org_id == current_user.org_id)
    )
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    if role:
        query = query.filter(Employee.role == role)
    if search:
        query = query.filter(
            Employee.name.ilike(f"%{search}%") | Employee.email.ilike(f"%{search}%")
        )
    return query.order_by(Employee.name).all()


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    req: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new employee profile."""
    existing = (
        db.query(Employee)
        .filter(Employee.org_id == current_user.org_id, Employee.email == req.email)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with email '{req.email}' already exists",
        )

    emp = Employee(
        org_id=current_user.org_id,
        name=req.name,
        email=req.email,
        role=req.role,
        cost_per_hour=req.cost_per_hour,
        weekly_capacity_hours=req.weekly_capacity_hours,
        max_overtime_hours=req.max_overtime_hours,
        start_date=req.start_date,
        end_date=req.end_date,
        career_goals=req.career_goals,
        is_active=req.is_active,
    )
    db.add(emp)
    db.flush()

    if req.skills:
        for sk in req.skills:
            emp_skill = EmployeeSkill(
                org_id=current_user.org_id,
                employee_id=emp.id,
                skill_id=sk.skill_id,
                proficiency=sk.proficiency,
                growth_target=sk.growth_target,
            )
            db.add(emp_skill)

    db.commit()
    db.refresh(emp)
    return emp


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = (
        db.query(Employee)
        .options(
            joinedload(Employee.skills).joinedload(EmployeeSkill.skill),
            joinedload(Employee.leaves),
        )
        .filter(Employee.id == employee_id, Employee.org_id == current_user.org_id)
        .first()
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    req: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = (
        db.query(Employee)
        .filter(Employee.id == employee_id, Employee.org_id == current_user.org_id)
        .first()
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(emp, field, val)

    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = (
        db.query(Employee)
        .filter(Employee.id == employee_id, Employee.org_id == current_user.org_id)
        .first()
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()


@router.post("/{employee_id}/skills", response_model=EmployeeSkillResponse)
def upsert_employee_skill(
    employee_id: str,
    req: EmployeeSkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add or update an employee's proficiency in a specific skill."""
    emp = (
        db.query(Employee)
        .filter(Employee.id == employee_id, Employee.org_id == current_user.org_id)
        .first()
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    skill = (
        db.query(Skill)
        .filter(Skill.id == req.skill_id, Skill.org_id == current_user.org_id)
        .first()
    )
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing = (
        db.query(EmployeeSkill)
        .filter(
            EmployeeSkill.employee_id == employee_id,
            EmployeeSkill.skill_id == req.skill_id,
        )
        .first()
    )

    if existing:
        existing.proficiency = req.proficiency
        existing.growth_target = req.growth_target
        item = existing
    else:
        item = EmployeeSkill(
            org_id=current_user.org_id,
            employee_id=employee_id,
            skill_id=req.skill_id,
            proficiency=req.proficiency,
            growth_target=req.growth_target,
        )
        db.add(item)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{employee_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_skill(
    employee_id: str,
    skill_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(EmployeeSkill)
        .filter(
            EmployeeSkill.employee_id == employee_id,
            EmployeeSkill.skill_id == skill_id,
            EmployeeSkill.org_id == current_user.org_id,
        )
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Employee skill record not found")
    db.delete(existing)
    db.commit()


@router.post("/{employee_id}/leaves", response_model=EmployeeLeaveResponse, status_code=status.HTTP_201_CREATED)
def add_employee_leave(
    employee_id: str,
    req: EmployeeLeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record an upcoming employee leave period."""
    emp = (
        db.query(Employee)
        .filter(Employee.id == employee_id, Employee.org_id == current_user.org_id)
        .first()
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    leave = EmployeeLeave(
        org_id=current_user.org_id,
        employee_id=employee_id,
        start_date=req.start_date,
        end_date=req.end_date,
        type=req.type,
        description=req.description,
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


@router.delete("/{employee_id}/leaves/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_leave(
    employee_id: str,
    leave_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    leave = (
        db.query(EmployeeLeave)
        .filter(
            EmployeeLeave.id == leave_id,
            EmployeeLeave.employee_id == employee_id,
            EmployeeLeave.org_id == current_user.org_id,
        )
        .first()
    )
    if not leave:
        raise HTTPException(status_code=404, detail="Leave record not found")
    db.delete(leave)
    db.commit()
