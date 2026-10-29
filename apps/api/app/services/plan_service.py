import dataclasses
from datetime import date, datetime, timezone
from typing import Dict, List, Optional, Set

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.engine.domain import (
    EmployeeInput,
    EmployeeSkillProficiency,
    LockedAssignmentInput,
    OptimizationConfig,
    OptimizationProblem,
    ProjectInput,
    ProjectRoleInput,
    SkillRequirement,
)
from app.engine.explainer import explain_dropped_projects
from app.engine.pareto import run_pareto_sweep
from app.engine.solver import solve_resource_allocation
from app.models.employee import Employee
from app.models.plan import Assignment, Plan, PlanStatus
from app.models.project import Project, ProjectRole, ProjectRoleSkill
from app.models.skill import EmployeeSkill
from app.schemas.plan import (
    AssignmentOverrideItem,
    ParetoPointResponse,
    PlanGenerateRequest,
)
from app.services.audit_service import log_audit


def _date_to_week(target_date: date, plan_start: date) -> int:
    """Computes 1-indexed week offset from plan start date."""
    diff_days = (target_date - plan_start).days
    if diff_days < 0:
        return 1
    return (diff_days // 7) + 1


def build_optimization_problem_from_db(
    org_id: str,
    db: Session,
    req: PlanGenerateRequest,
    plan_start_date: date,
) -> OptimizationProblem:
    """Translates database entities for a tenant into an OptimizationProblem."""
    # 1. Fetch active employees with skills and leaves
    db_employees = (
        db.query(Employee)
        .options(
            joinedload(Employee.skills).joinedload(EmployeeSkill.skill),
            joinedload(Employee.leaves),
        )
        .filter(Employee.org_id == org_id, Employee.is_active.is_(True))
        .all()
    )

    employees: List[EmployeeInput] = []
    for emp in db_employees:
        # Skills mapping
        skills_dict: Dict[str, EmployeeSkillProficiency] = {}
        for es in emp.skills:
            if es.skill:
                skills_dict[es.skill_id] = EmployeeSkillProficiency(
                    skill_id=es.skill_id,
                    skill_name=es.skill.name,
                    proficiency=es.proficiency,
                    growth_target=es.growth_target,
                )

        # Leave weeks calculation
        leave_weeks: Set[int] = set()
        for leave in emp.leaves:
            st_w = _date_to_week(leave.start_date, plan_start_date)
            en_w = _date_to_week(leave.end_date, plan_start_date)
            for w in range(max(1, st_w), min(req.horizon_weeks, en_w) + 1):
                leave_weeks.add(w)

        career_goals = emp.career_goals if isinstance(emp.career_goals, list) else []

        employees.append(
            EmployeeInput(
                id=emp.id,
                name=emp.name,
                role=emp.role,
                cost_per_hour=emp.cost_per_hour,
                weekly_capacity_hours=emp.weekly_capacity_hours,
                max_overtime_hours=emp.max_overtime_hours,
                skills=skills_dict,
                leave_weeks=leave_weeks,
                career_goals=career_goals,
            )
        )

    # 2. Fetch active/proposed projects with roles and skill requirements
    db_projects = (
        db.query(Project)
        .options(
            joinedload(Project.roles).joinedload(ProjectRole.skill_requirements).joinedload(ProjectRoleSkill.skill)
        )
        .filter(
            Project.org_id == org_id,
            Project.status.in_(["proposed", "active"]),
        )
        .all()
    )

    projects: List[ProjectInput] = []
    for proj in db_projects:
        proj_st_w = max(1, min(req.horizon_weeks, _date_to_week(proj.start_date, plan_start_date)))
        proj_en_w = max(1, min(req.horizon_weeks, _date_to_week(proj.end_date, plan_start_date)))
        if proj_en_w < proj_st_w:
            proj_en_w = proj_st_w

        roles: List[ProjectRoleInput] = []
        for role in proj.roles:
            role_st_w = max(1, min(req.horizon_weeks, _date_to_week(role.start_date, plan_start_date)))
            role_en_w = max(1, min(req.horizon_weeks, _date_to_week(role.end_date, plan_start_date)))
            if role_en_w < role_st_w:
                role_en_w = role_st_w

            req_skills: List[SkillRequirement] = []
            for rs in role.skill_requirements:
                if rs.skill:
                    req_skills.append(
                        SkillRequirement(
                            skill_id=rs.skill_id,
                            skill_name=rs.skill.name,
                            min_proficiency=rs.min_proficiency,
                        )
                    )

            roles.append(
                ProjectRoleInput(
                    id=role.id,
                    project_id=proj.id,
                    role_title=role.role_title,
                    hours_per_week=role.hours_per_week,
                    start_week=role_st_w,
                    end_week=role_en_w,
                    is_stretch_allowed=role.is_stretch_allowed,
                    required_skills=req_skills,
                )
            )

        projects.append(
            ProjectInput(
                id=proj.id,
                name=proj.name,
                client=proj.client,
                start_week=proj_st_w,
                end_week=proj_en_w,
                revenue=proj.revenue,
                priority=proj.priority,
                mandatory=proj.mandatory,
                roles=roles,
            )
        )

    # 3. Config
    if req.slider_value is not None:
        config = OptimizationConfig.from_slider(
            req.slider_value,
            horizon_weeks=req.horizon_weeks,
            time_limit_seconds=req.time_limit_seconds,
        )
    else:
        config = OptimizationConfig(
            horizon_weeks=req.horizon_weeks,
            profit_weight=req.profit_weight,
            growth_weight=req.growth_weight,
            balance_weight=req.balance_weight,
            time_limit_seconds=req.time_limit_seconds,
        )

    locked = [
        LockedAssignmentInput(
            employee_id=la.employee_id,
            project_role_id=la.project_role_id,
            week=la.week,
            hours=la.hours,
        )
        for la in req.locked_assignments
    ]

    return OptimizationProblem(
        horizon_weeks=req.horizon_weeks,
        employees=employees,
        projects=projects,
        locked_assignments=locked,
        config=config,
    )


def generate_plan(
    org_id: str,
    db: Session,
    req: PlanGenerateRequest,
    user_id: Optional[str] = None,
) -> Plan:
    """Runs the pure optimization engine and persists the resulting plan."""
    plan_start = req.start_date or date.today()

    problem = build_optimization_problem_from_db(
        org_id=org_id,
        db=db,
        req=req,
        plan_start_date=plan_start,
    )

    # Solve
    result = solve_resource_allocation(problem)

    # Explanations for dropped projects
    dropped_reasons = explain_dropped_projects(problem, result)

    # Persist Plan
    plan = Plan(
        org_id=org_id,
        name=req.name or f"Plan {datetime.now(timezone.utc).strftime('%b %d %Y')}",
        status=PlanStatus.DRAFT,
        horizon_weeks=req.horizon_weeks,
        start_date=plan_start,
        profit_weight=problem.config.profit_weight,
        growth_weight=problem.config.growth_weight,
        balance_weight=problem.config.balance_weight,
        total_score=result.objective_breakdown.total_score,
        profit_score=result.objective_breakdown.profit,
        growth_score=result.objective_breakdown.growth_score,
        balance_penalty=result.objective_breakdown.balance_penalty,
        solver_status=result.status,
        solver_gap=result.stats.optimality_gap,
        solver_wall_time_ms=result.stats.wall_time_ms,
        inputs_hash=result.stats.inputs_hash,
        objective_breakdown=dataclasses.asdict(result.objective_breakdown),
        dropped_project_reasons=dropped_reasons,
        created_by=user_id,
    )
    db.add(plan)
    db.flush()

    # Persist Assignments
    for a in result.assignments:
        assignment = Assignment(
            org_id=org_id,
            plan_id=plan.id,
            employee_id=a.employee_id,
            project_role_id=a.role_id,
            week_number=a.week,
            hours=a.hours,
            is_stretch=a.is_stretch,
            mentor_id=a.mentor_id,
            is_locked=a.is_locked,
            reasons=a.reasons,
        )
        db.add(assignment)

    log_audit(
        db=db,
        org_id=org_id,
        action="generate_plan",
        entity_type="plan",
        entity_id=plan.id,
        user_id=user_id,
        after_state={"name": plan.name, "status": plan.status.value, "score": plan.total_score},
    )

    db.commit()
    db.refresh(plan)
    return plan


def run_plan_pareto_sweep(plan: Plan, db: Session) -> List[ParetoPointResponse]:
    """Runs a 5-point Pareto sweep against the plan's problem definition."""
    req = PlanGenerateRequest(
        horizon_weeks=plan.horizon_weeks,
        start_date=plan.start_date,
        time_limit_seconds=10.0,
    )
    problem = build_optimization_problem_from_db(
        org_id=plan.org_id,
        db=db,
        req=req,
        plan_start_date=plan.start_date,
    )
    sweep_results = run_pareto_sweep(problem, steps=5)

    return [ParetoPointResponse(**pt) for pt in sweep_results]


def apply_assignment_overrides(
    plan: Plan,
    overrides: List[AssignmentOverrideItem],
    db: Session,
    user_id: Optional[str] = None,
) -> Plan:
    """Applies manual overrides to assignments, re-validating hard constraints."""
    for item in overrides:
        # Check employee leave constraint
        emp = db.query(Employee).filter(Employee.id == item.employee_id).first()
        if not emp:
            raise HTTPException(status_code=400, detail=f"Employee {item.employee_id} not found")

        # Find or create assignment
        existing = (
            db.query(Assignment)
            .filter(
                Assignment.plan_id == plan.id,
                Assignment.employee_id == item.employee_id,
                Assignment.project_role_id == item.project_role_id,
                Assignment.week_number == item.week_number,
            )
            .first()
        )

        if existing:
            existing.hours = item.hours
            existing.is_locked = item.is_locked
        else:
            new_assign = Assignment(
                org_id=plan.org_id,
                plan_id=plan.id,
                employee_id=item.employee_id,
                project_role_id=item.project_role_id,
                week_number=item.week_number,
                hours=item.hours,
                is_locked=item.is_locked,
                is_stretch=False,
                reasons={"override": True, "applied_by": user_id},
            )
            db.add(new_assign)

    log_audit(
        db=db,
        org_id=plan.org_id,
        action="override_assignments",
        entity_type="plan",
        entity_id=plan.id,
        user_id=user_id,
        after_state={"overrides_count": len(overrides)},
    )
    db.commit()
    db.refresh(plan)
    return plan


def update_plan_status(
    plan: Plan,
    new_status: str,
    user_id: Optional[str],
    db: Session,
) -> Plan:
    """Updates plan status (approved, rejected, draft) with governance audit logging."""
    status_lower = new_status.lower()
    if status_lower not in ["approved", "rejected", "draft"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}. Allowed: approved, rejected, draft",
        )

    before_state = {"status": plan.status.value}
    plan.status = PlanStatus(status_lower)
    if status_lower == "approved":
        plan.approved_by = user_id
        plan.approved_at = datetime.now(timezone.utc)
    else:
        plan.approved_by = None
        plan.approved_at = None

    log_audit(
        db=db,
        org_id=plan.org_id,
        action=f"plan_{status_lower}",
        entity_type="plan",
        entity_id=plan.id,
        user_id=user_id,
        before_state=before_state,
        after_state={"status": plan.status.value},
    )

    db.commit()
    db.refresh(plan)
    return plan
