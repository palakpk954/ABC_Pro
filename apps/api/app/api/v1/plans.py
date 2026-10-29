from typing import List, Dict, Any
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_org_id, RoleChecker
from app.models import (
    Plan,
    PlanStatus,
    Assignment,
    Scenario,
    User,
    UserRole,
)
from app.schemas.plan import (
    PlanGenerateRequest,
    PlanResponse,
    AssignmentResponse,
    AssignmentOverrideRequest,
    ScenarioCreateRequest,
    ScenarioResponse,
    ParetoResponse,
    ParetoPoint,
)
from app.engine.domain import (
    OptimizationConfig,
    LockedAssignmentInput,
)
from app.engine.pareto import run_pareto_sweep
from app.services.jobs import job_runner
from app.services.plan_service import (
    load_problem_for_org,
    execute_plan_generation,
    validate_and_apply_override,
    create_scenario_with_diff,
)
from app.services.audit import log_audit_event

router = APIRouter(prefix="/plans", tags=["Plans"])


def format_plan_response(p: Plan) -> PlanResponse:
    assignments_resp = [
        AssignmentResponse(
            id=a.id,
            employee_id=a.employee_id,
            employee_name=a.employee.name if a.employee else None,
            project_id=a.project_role.project_id if a.project_role else None,
            project_name=a.project_role.project.name if a.project_role and a.project_role.project else None,
            project_role_id=a.project_role_id,
            role_title=a.project_role.role_title if a.project_role else None,
            week_number=a.week_number,
            hours=a.hours,
            is_stretch=a.is_stretch,
            mentor_id=a.mentor_id,
            mentor_name=a.mentor.name if a.mentor else None,
            is_locked=a.is_locked,
            reasons=a.reasons,
        )
        for a in p.assignments
    ]

    return PlanResponse(
        id=p.id,
        org_id=p.org_id,
        name=p.name,
        status=p.status.value if hasattr(p.status, "value") else str(p.status),
        horizon_weeks=p.horizon_weeks,
        start_date=p.start_date,
        profit_weight=p.profit_weight,
        growth_weight=p.growth_weight,
        balance_weight=p.balance_weight,
        total_score=p.total_score,
        profit_score=p.profit_score,
        growth_score=p.growth_score,
        balance_penalty=p.balance_penalty,
        solver_status=p.solver_status,
        solver_gap=p.solver_gap,
        solver_wall_time_ms=p.solver_wall_time_ms,
        inputs_hash=p.inputs_hash,
        objective_breakdown=p.objective_breakdown,
        dropped_project_reasons=p.dropped_project_reasons,
        created_by=p.created_by,
        approved_by=p.approved_by,
        approved_at=p.approved_at,
        created_at=p.created_at,
        updated_at=p.updated_at,
        assignments=assignments_resp,
    )


@router.get("", response_model=List[PlanResponse])
def list_plans(
    db: Session = Depends(get_db),
    org_id: str = Depends(get_current_org_id),
):
    plans = db.query(Plan).filter(Plan.org_id == org_id).order_by(Plan.created_at.desc()).all()
    return [format_plan_response(p) for p in plans]


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_plan(
    req: PlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Triggers asynchronous optimization job and returns tracking job ID and draft plan ID."""
    ref_start = req.start_date or date(2026, 11, 2)

    if req.slider_value is not None:
        cfg = OptimizationConfig.from_slider(
            slider_value=req.slider_value,
            horizon_weeks=req.horizon_weeks,
            time_limit_seconds=req.solver_time_limit_seconds,
        )
    else:
        cfg = OptimizationConfig(
            horizon_weeks=req.horizon_weeks,
            profit_weight=req.profit_weight or 0.6,
            growth_weight=req.growth_weight or 0.3,
            balance_weight=req.balance_weight or 0.1,
            time_limit_seconds=req.solver_time_limit_seconds,
        )

    # Create initial draft plan record
    plan = Plan(
        org_id=current_user.org_id,
        name=req.name or "Staffing Plan",
        status=PlanStatus.DRAFT,
        horizon_weeks=req.horizon_weeks,
        start_date=ref_start,
        profit_weight=cfg.profit_weight,
        growth_weight=cfg.growth_weight,
        balance_weight=cfg.balance_weight,
        created_by=current_user.id,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    locked_inputs = [
        LockedAssignmentInput(
            employee_id=l.employee_id,
            project_role_id=l.project_role_id,
            week=l.week,
            hours=l.hours,
        )
        for l in req.locked_assignments
    ]

    # Submit background optimization job
    job_id = job_runner.submit_job(
        target_func=execute_plan_generation,
        plan_id=plan.id,
        org_id=current_user.org_id,
        user_id=current_user.id,
        config=cfg,
        locked_assignments=locked_inputs,
    )

    return {
        "job_id": job_id,
        "plan_id": plan.id,
        "status": "PENDING",
        "message": f"Optimization started with time limit {cfg.time_limit_seconds}s.",
    }


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    org_id: str = Depends(get_current_org_id),
):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.org_id == org_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return format_plan_response(plan)


@router.patch("/{plan_id}/assignments")
def override_assignment(
    plan_id: str,
    override_in: AssignmentOverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually overrides an assignment, re-validates hard constraints, and re-scores."""
    try:
        res = validate_and_apply_override(
            db=db,
            org_id=current_user.org_id,
            user_id=current_user.id,
            assignment_id=override_in.assignment_id,
            new_employee_id=override_in.employee_id,
            new_hours=override_in.hours,
            is_locked=override_in.is_locked,
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{plan_id}/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(
    plan_id: str,
    scenario_in: ScenarioCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generates what-if scenario solve and returns side-by-side diff against base plan."""
    try:
        scenario = create_scenario_with_diff(
            db=db,
            base_plan_id=plan_id,
            org_id=current_user.org_id,
            user_id=current_user.id,
            name=scenario_in.name,
            description=scenario_in.description,
            modifications=scenario_in.modifications,
        )
        return scenario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{plan_id}/approve")
def approve_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.DELIVERY_HEAD, UserRole.ADMIN])),
):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.org_id == current_user.org_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    before_status = plan.status.value if hasattr(plan.status, "value") else str(plan.status)
    plan.status = PlanStatus.APPROVED
    plan.approved_by = current_user.id
    plan.approved_at = datetime.now(timezone.utc)
    db.commit()

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="approve_plan",
        entity_type="plan",
        entity_id=plan.id,
        before_state={"status": before_status},
        after_state={"status": "approved", "approved_by": current_user.id},
    )
    db.commit()

    return {"message": "Plan successfully approved", "plan_id": plan.id, "status": "approved"}


@router.post("/{plan_id}/reject")
def reject_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.DELIVERY_HEAD, UserRole.ADMIN])),
):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.org_id == current_user.org_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    before_status = plan.status.value if hasattr(plan.status, "value") else str(plan.status)
    plan.status = PlanStatus.REJECTED
    db.commit()

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="reject_plan",
        entity_type="plan",
        entity_id=plan.id,
        before_state={"status": before_status},
        after_state={"status": "rejected"},
    )
    db.commit()

    return {"message": "Plan rejected", "plan_id": plan.id, "status": "rejected"}


@router.get("/{plan_id}/pareto", response_model=ParetoResponse)
def get_plan_pareto_curve(
    plan_id: str,
    db: Session = Depends(get_db),
    org_id: str = Depends(get_current_org_id),
):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.org_id == org_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    cfg = OptimizationConfig(
        horizon_weeks=plan.horizon_weeks,
        time_limit_seconds=10.0,
    )
    prob = load_problem_for_org(db, org_id, cfg, planning_start_date=plan.start_date)

    curve_raw = run_pareto_sweep(prob, steps=5)
    points = [ParetoPoint(**pt) for pt in curve_raw]

    return ParetoResponse(plan_id=plan.id, curve=points)
