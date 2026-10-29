from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_org_id
from app.models import Employee, EmployeeSkill, EmployeeLeave, Skill, User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeLeaveCreate,
    EmployeeLeaveResponse,
)
from app.schemas.skill import EmployeeSkillCreate, EmployeeSkillResponse
from app.services.audit import log_audit_event

router = APIRouter(prefix="/employees", tags=["Employees"])


def format_employee_response(emp: Employee) -> EmployeeResponse:
    skills_resp = [
        EmployeeSkillResponse(
            id=es.id,
            employee_id=es.employee_id,
            skill_id=es.skill_id,
            skill_name=es.skill.name if es.skill else None,
            skill_category=es.skill.category if es.skill else None,
            proficiency=es.proficiency,
            growth_target=es.growth_target,
        )
        for es in emp.skills
    ]
    leaves_resp = [
        EmployeeLeaveResponse(
            id=lv.id,
            employee_id=lv.employee_id,
            start_date=lv.start_date,
            end_date=lv.end_date,
            reason=lv.reason,
        )
        for lv in emp.leaves
    ]
    return EmployeeResponse(
        id=emp.id,
        org_id=emp.org_id,
        name=emp.name,
        email=emp.email,
        role=emp.role,
        cost_per_hour=emp.cost_per_hour,
        weekly_capacity_hours=emp.weekly_capacity_hours,
        max_overtime_hours=emp.max_overtime_hours,
        start_date=emp.start_date,
        end_date=emp.end_date,
        career_goals=emp.career_goals or [],
        is_active=emp.is_active,
        skills=skills_resp,
        leaves=leaves_resp,
    )


@router.get("", response_model=List[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    org_id: str = Depends(get_current_org_id),
):
    employees = db.query(Employee).filter(Employee.org_id == org_id).all()
    return [format_employee_response(e) for e in employees]


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    emp_in: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Employee).filter(
        Employee.org_id == current_user.org_id,
        Employee.email == emp_in.email,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee with this email already exists")

    emp = Employee(
        org_id=current_user.org_id,
        name=emp_in.name,
        email=emp_in.email,
        role=emp_in.role,
        cost_per_hour=emp_in.cost_per_hour,
        weekly_capacity_hours=emp_in.weekly_capacity_hours,
        max_overtime_hours=emp_in.max_overtime_hours,
        start_date=emp_in.start_date,
        end_date=emp_in.end_date,
        career_goals=emp_in.career_goals,
        is_active=emp_in.is_active,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="create",
        entity_type="employee",
        entity_id=emp.id,
        after_state={"name": emp.name, "email": emp.email, "role": emp.role},
    )
    db.commit()

    return format_employee_response(emp)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    org_id: str = Depends(get_current_org_id),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.org_id == org_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return format_employee_response(emp)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    emp_in: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.org_id == current_user.org_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    before_state = {"name": emp.name, "role": emp.role, "cost_per_hour": emp.cost_per_hour}

    if emp_in.name is not None:
        emp.name = emp_in.name
    if emp_in.email is not None:
        emp.email = emp_in.email
    if emp_in.role is not None:
        emp.role = emp_in.role
    if emp_in.cost_per_hour is not None:
        emp.cost_per_hour = emp_in.cost_per_hour
    if emp_in.weekly_capacity_hours is not None:
        emp.weekly_capacity_hours = emp_in.weekly_capacity_hours
    if emp_in.max_overtime_hours is not None:
        emp.max_overtime_hours = emp_in.max_overtime_hours
    if emp_in.start_date is not None:
        emp.start_date = emp_in.start_date
    if emp_in.end_date is not None:
        emp.end_date = emp_in.end_date
    if emp_in.career_goals is not None:
        emp.career_goals = emp_in.career_goals
    if emp_in.is_active is not None:
        emp.is_active = emp_in.is_active

    db.commit()
    db.refresh(emp)

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="update",
        entity_type="employee",
        entity_id=emp.id,
        before_state=before_state,
        after_state={"name": emp.name, "role": emp.role, "cost_per_hour": emp.cost_per_hour},
    )
    db.commit()

    return format_employee_response(emp)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.org_id == current_user.org_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="delete",
        entity_type="employee",
        entity_id=employee_id,
        before_state={"name": emp.name},
    )
    db.commit()


# Employee Skills Sub-endpoints
@router.post("/{employee_id}/skills", response_model=EmployeeSkillResponse, status_code=status.HTTP_201_CREATED)
def assign_employee_skill(
    employee_id: str,
    skill_in: EmployeeSkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.org_id == current_user.org_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    skill = db.query(Skill).filter(Skill.id == skill_in.skill_id, Skill.org_id == current_user.org_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    emp_skill = db.query(EmployeeSkill).filter(
        EmployeeSkill.org_id == current_user.org_id,
        EmployeeSkill.employee_id == employee_id,
        EmployeeSkill.skill_id == skill_in.skill_id,
    ).first()

    if emp_skill:
        emp_skill.proficiency = skill_in.proficiency
        emp_skill.growth_target = skill_in.growth_target
    else:
        emp_skill = EmployeeSkill(
            org_id=current_user.org_id,
            employee_id=employee_id,
            skill_id=skill_in.skill_id,
            proficiency=skill_in.proficiency,
            growth_target=skill_in.growth_target,
        )
        db.add(emp_skill)

    db.commit()
    db.refresh(emp_skill)

    return EmployeeSkillResponse(
        id=emp_skill.id,
        employee_id=emp_skill.employee_id,
        skill_id=emp_skill.skill_id,
        skill_name=skill.name,
        skill_category=skill.category,
        proficiency=emp_skill.proficiency,
        growth_target=emp_skill.growth_target,
    )


# Employee Leaves Sub-endpoints
@router.post("/{employee_id}/leaves", response_model=EmployeeLeaveResponse, status_code=status.HTTP_201_CREATED)
def add_employee_leave(
    employee_id: str,
    leave_in: EmployeeLeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.org_id == current_user.org_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    if leave_in.start_date > leave_in.end_date:
        raise HTTPException(status_code=400, detail="Leave start date cannot be after end date")

    leave = EmployeeLeave(
        org_id=current_user.org_id,
        employee_id=employee_id,
        start_date=leave_in.start_date,
        end_date=leave_in.end_date,
        reason=leave_in.reason,
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="create_leave",
        entity_type="employee_leave",
        entity_id=leave.id,
        after_state={"employee_id": employee_id, "start_date": str(leave.start_date), "end_date": str(leave.end_date)},
    )
    db.commit()

    return leave
