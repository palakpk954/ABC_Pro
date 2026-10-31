from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.employee import Employee
from app.models.plan import Plan
from app.models.project import Project, ProjectRole
from app.models.user import User
from app.schemas.plan import (
    AssignmentOverrideRequest,
    AssignmentResponse,
    ParetoPointResponse,
    PlanChatRequest,
    PlanChatResponse,
    PlanDetailResponse,
    PlanGenerateRequest,
    PlanSummaryResponse,
)
from app.services.plan_service import (
    apply_assignment_overrides,
    generate_plan,
    run_plan_pareto_sweep,
    update_plan_status,
)

router = APIRouter()


def _hydrate_plan_detail(plan: Plan, db: Session) -> PlanDetailResponse:
    """Builds a rich PlanDetailResponse hydrating entity names and explanations."""
    # Pre-fetch lookup dictionaries
    emp_map = {e.id: e for e in db.query(Employee).filter(Employee.org_id == plan.org_id).all()}
    role_map = {r.id: r for r in db.query(ProjectRole).filter(ProjectRole.org_id == plan.org_id).all()}
    proj_map = {p.id: p for p in db.query(Project).filter(Project.org_id == plan.org_id).all()}

    assignments_out: List[AssignmentResponse] = []
    for a in plan.assignments:
        emp = emp_map.get(a.employee_id)
        role = role_map.get(a.project_role_id)
        proj = proj_map.get(role.project_id) if role else None
        mentor = emp_map.get(a.mentor_id) if a.mentor_id else None

        assignments_out.append(
            AssignmentResponse(
                id=a.id,
                plan_id=a.plan_id,
                employee_id=a.employee_id,
                employee_name=emp.name if emp else "Unknown",
                employee_role=emp.role if emp else "",
                project_role_id=a.project_role_id,
                project_id=proj.id if proj else None,
                project_name=proj.name if proj else None,
                role_title=role.role_title if role else None,
                week_number=a.week_number,
                hours=a.hours,
                is_stretch=a.is_stretch,
                mentor_id=a.mentor_id,
                mentor_name=mentor.name if mentor else None,
                is_locked=a.is_locked,
                reasons=a.reasons,
            )
        )

    return PlanDetailResponse(
        id=plan.id,
        org_id=plan.org_id,
        name=plan.name,
        status=plan.status.value,
        horizon_weeks=plan.horizon_weeks,
        start_date=plan.start_date,
        profit_weight=plan.profit_weight,
        growth_weight=plan.growth_weight,
        balance_weight=plan.balance_weight,
        total_score=plan.total_score,
        profit_score=plan.profit_score,
        growth_score=plan.growth_score,
        balance_penalty=plan.balance_penalty,
        solver_status=plan.solver_status,
        solver_gap=plan.solver_gap,
        solver_wall_time_ms=plan.solver_wall_time_ms,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        objective_breakdown=plan.objective_breakdown,
        dropped_project_reasons=plan.dropped_project_reasons,
        assignments=assignments_out,
        created_by=plan.created_by,
        approved_by=plan.approved_by,
        approved_at=plan.approved_at,
    )


@router.post("/generate", response_model=PlanDetailResponse, status_code=status.HTTP_201_CREATED)
def generate_new_plan(
    req: PlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger pure OR-Tools optimization engine and persist new staffing plan."""
    plan = generate_plan(
        org_id=current_user.org_id,
        db=db,
        req=req,
        user_id=current_user.id,
    )
    return _hydrate_plan_detail(plan, db)


@router.get("", response_model=List[PlanSummaryResponse])
def list_plans(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List plans generated for organization."""
    query = db.query(Plan).filter(Plan.org_id == current_user.org_id)
    if status:
        query = query.filter(Plan.status == status)
    return query.order_by(Plan.created_at.desc()).all()


@router.get("/{plan_id}", response_model=PlanDetailResponse)
def get_plan_details(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch complete plan details with assignments and structured explanations."""
    plan = (
        db.query(Plan)
        .options(joinedload(Plan.assignments))
        .filter(Plan.id == plan_id, Plan.org_id == current_user.org_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return _hydrate_plan_detail(plan, db)


@router.get("/{plan_id}/pareto", response_model=List[ParetoPointResponse])
def get_plan_pareto_curve(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Computes a 5-point Pareto tradeoff sweep (profit vs growth) for the plan."""
    plan = (
        db.query(Plan)
        .filter(Plan.id == plan_id, Plan.org_id == current_user.org_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return run_plan_pareto_sweep(plan, db)


@router.post("/{plan_id}/overrides", response_model=PlanDetailResponse)
def apply_overrides(
    plan_id: str,
    req: AssignmentOverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Apply manual manager overrides to specific assignments."""
    plan = (
        db.query(Plan)
        .options(joinedload(Plan.assignments))
        .filter(Plan.id == plan_id, Plan.org_id == current_user.org_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    updated_plan = apply_assignment_overrides(
        plan=plan,
        overrides=req.overrides,
        db=db,
        user_id=current_user.id,
    )
    return _hydrate_plan_detail(updated_plan, db)


@router.post("/{plan_id}/approve", response_model=PlanDetailResponse)
def approve_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve a draft plan with immutable governance audit trail."""
    plan = (
        db.query(Plan)
        .options(joinedload(Plan.assignments))
        .filter(Plan.id == plan_id, Plan.org_id == current_user.org_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    updated_plan = update_plan_status(
        plan=plan,
        new_status="approved",
        user_id=current_user.id,
        db=db,
    )
    return _hydrate_plan_detail(updated_plan, db)


@router.post("/{plan_id}/reject", response_model=PlanDetailResponse)
def reject_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a plan with immutable governance audit trail."""
    plan = (
        db.query(Plan)
        .options(joinedload(Plan.assignments))
        .filter(Plan.id == plan_id, Plan.org_id == current_user.org_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    updated_plan = update_plan_status(
        plan=plan,
        new_status="rejected",
        user_id=current_user.id,
        db=db,
    )
    return _hydrate_plan_detail(updated_plan, db)


@router.get("/{plan_id}/advisory")
def get_plan_advisory(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cognitive Resource Manager advisory and natural executive commentary for a plan.
    Emulates an empathetic, commercially astute RM examining margins, burnout, stretch learning,
    and mentorship chemistry.
    """
    plan = (
        db.query(Plan)
        .options(
            joinedload(Plan.assignments).joinedload(Assignment.employee).joinedload(Employee.dossier),
            joinedload(Plan.assignments).joinedload(Assignment.mentor),
            joinedload(Plan.assignments).joinedload(Assignment.project_role).joinedload(ProjectRole.project),
        )
        .filter(Plan.id == plan_id, Plan.org_id == current_user.org_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    from app.services.cognitive_advisor import CognitiveAdvisorService
    return CognitiveAdvisorService.generate_plan_advisory(plan=plan, db=db)


@router.post("/{plan_id}/chat", response_model=PlanChatResponse)
def chat_with_advisor(
    plan_id: str,
    req: PlanChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Interactive conversation with AI Resource Manager 'Alex'.
    Answers questions on staffing rationale, burnout mitigation, margin health,
    and What-If scenarios with living dossier citations.
    """
    plan = (
        db.query(Plan)
        .options(
            joinedload(Plan.assignments).joinedload(Assignment.employee).joinedload(Employee.dossier),
            joinedload(Plan.assignments).joinedload(Assignment.mentor),
            joinedload(Plan.assignments).joinedload(Assignment.project_role).joinedload(ProjectRole.project),
        )
        .filter(Plan.id == plan_id, Plan.org_id == current_user.org_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    from app.services.cognitive_advisor import CognitiveAdvisorService
    history_dicts = (
        [{"role": msg.role, "content": msg.content} for msg in req.history]
        if req.history
        else None
    )
    return CognitiveAdvisorService.answer_advisor_query(
        plan=plan,
        query=req.query,
        history=history_dicts,
        db=db,
    )

