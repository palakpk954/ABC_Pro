"""Plan, Assignment Override, and Scenario Management Service

Handles loading optimization models from database, executing solver runs,
persisting versioned plans, validating manual overrides, and computing what-if diffs.
"""

from typing import Dict, List, Set, Optional, Any
from datetime import date
from copy import deepcopy
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import (
    Plan,
    PlanStatus,
    Assignment,
    Scenario,
    Employee,
    Project,
)
from app.engine.domain import (
    OptimizationProblem,
    OptimizationConfig,
    EmployeeInput,
    EmployeeSkillProficiency,
    ProjectInput,
    ProjectRoleInput,
    SkillRequirement,
    LockedAssignmentInput,
)
from app.engine.solver import solve_resource_allocation
from app.engine.explainer import explain_dropped_projects
from app.engine.pre_solve import is_employee_qualified_for_role
from app.services.audit import log_audit_event


def load_problem_for_org(
    db: Session,
    org_id: str,
    config: OptimizationConfig,
    locked_assignments: Optional[List[LockedAssignmentInput]] = None,
    planning_start_date: Optional[date] = None,
) -> OptimizationProblem:
    ref_start = planning_start_date or date(2026, 11, 2)
    horizon_weeks = config.horizon_weeks

    # 1. Load Employees
    db_employees = db.query(Employee).filter(Employee.org_id == org_id, Employee.is_active).all()
    employees: List[EmployeeInput] = []

    for e in db_employees:
        skills_dict: Dict[str, EmployeeSkillProficiency] = {}
        for es in e.skills:
            skills_dict[es.skill_id] = EmployeeSkillProficiency(
                skill_id=es.skill_id,
                skill_name=es.skill.name,
                proficiency=es.proficiency,
                growth_target=es.growth_target,
            )

        leave_weeks: Set[int] = set()
        for lv in e.leaves:
            wk_start = ((lv.start_date - ref_start).days // 7) + 1
            wk_end = ((lv.end_date - ref_start).days // 7) + 1
            for w in range(max(1, wk_start), min(horizon_weeks + 1, wk_end + 1)):
                leave_weeks.add(w)

        employees.append(
            EmployeeInput(
                id=e.id,
                name=e.name,
                role=e.role,
                cost_per_hour=e.cost_per_hour,
                weekly_capacity_hours=e.weekly_capacity_hours,
                max_overtime_hours=e.max_overtime_hours,
                skills=skills_dict,
                leave_weeks=leave_weeks,
                career_goals=e.career_goals or [],
            )
        )

    # 2. Load Projects
    db_projects = db.query(Project).filter(Project.org_id == org_id).all()
    projects: List[ProjectInput] = []

    for p in db_projects:
        roles_input: List[ProjectRoleInput] = []
        p_start_wk = max(1, ((p.start_date - ref_start).days // 7) + 1)
        p_end_wk = min(horizon_weeks, ((p.end_date - ref_start).days // 7) + 1)

        for r in p.roles:
            req_skills = [
                SkillRequirement(
                    skill_id=prs.skill_id,
                    skill_name=prs.skill.name,
                    min_proficiency=prs.min_proficiency,
                )
                for prs in r.skill_requirements
            ]
            r_start_wk = max(1, ((r.start_date - ref_start).days // 7) + 1)
            r_end_wk = min(horizon_weeks, ((r.end_date - ref_start).days // 7) + 1)

            roles_input.append(
                ProjectRoleInput(
                    id=r.id,
                    project_id=p.id,
                    role_title=r.role_title,
                    hours_per_week=r.hours_per_week,
                    start_week=r_start_wk,
                    end_week=r_end_wk,
                    is_stretch_allowed=r.is_stretch_allowed,
                    required_skills=req_skills,
                )
            )

        projects.append(
            ProjectInput(
                id=p.id,
                name=p.name,
                client=p.client,
                start_week=p_start_wk,
                end_week=p_end_wk,
                revenue=p.revenue,
                priority=p.priority,
                mandatory=p.mandatory,
                roles=roles_input,
            )
        )

    return OptimizationProblem(
        horizon_weeks=horizon_weeks,
        employees=employees,
        projects=projects,
        locked_assignments=locked_assignments or [],
        config=config,
    )


def execute_plan_generation(
    plan_id: str,
    org_id: str,
    user_id: Optional[str],
    config: OptimizationConfig,
    locked_assignments: List[LockedAssignmentInput],
    db: Optional[Session] = None,
):
    """Worker task that runs optimization and persists results."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        plan = db.query(Plan).filter(Plan.id == plan_id, Plan.org_id == org_id).first()
        if not plan:
            return

        problem = load_problem_for_org(
            db=db,
            org_id=org_id,
            config=config,
            locked_assignments=locked_assignments,
            planning_start_date=plan.start_date,
        )

        result = solve_resource_allocation(problem)

        # Generate explanations for dropped projects
        dropped_explanations = explain_dropped_projects(problem, result)

        # Update Plan metadata and metrics
        plan.status = PlanStatus.DRAFT
        plan.total_score = result.objective_breakdown.total_score
        plan.profit_score = result.objective_breakdown.profit
        plan.growth_score = result.objective_breakdown.growth_score
        plan.balance_penalty = result.objective_breakdown.balance_penalty
        plan.solver_status = result.status
        plan.solver_gap = result.stats.optimality_gap
        plan.solver_wall_time_ms = result.stats.wall_time_ms
        plan.inputs_hash = result.stats.inputs_hash
        plan.objective_breakdown = {
            "total_score": result.objective_breakdown.total_score,
            "profit": result.objective_breakdown.profit,
            "revenue": result.objective_breakdown.revenue,
            "labor_cost": result.objective_breakdown.labor_cost,
            "overtime_cost": result.objective_breakdown.overtime_cost,
            "growth_score": result.objective_breakdown.growth_score,
            "skill_gap_closure_score": result.objective_breakdown.skill_gap_closure_score,
            "stretch_bonus": result.objective_breakdown.stretch_bonus,
            "mentor_bonus": result.objective_breakdown.mentor_bonus,
            "balance_penalty": result.objective_breakdown.balance_penalty,
        }
        plan.dropped_project_reasons = dropped_explanations

        # Delete old assignments if re-running
        db.query(Assignment).filter(Assignment.plan_id == plan.id).delete()

        # Insert new assignments
        for asgn in result.assignments:
            db_asgn = Assignment(
                org_id=org_id,
                plan_id=plan.id,
                employee_id=asgn.employee_id,
                project_role_id=asgn.role_id,
                week_number=asgn.week,
                hours=asgn.hours,
                is_stretch=asgn.is_stretch,
                mentor_id=asgn.mentor_id,
                is_locked=asgn.is_locked,
                reasons=asgn.reasons,
            )
            db.add(db_asgn)

        db.commit()

        log_audit_event(
            db=db,
            org_id=org_id,
            user_id=user_id,
            action="generate_plan",
            entity_type="plan",
            entity_id=plan.id,
            after_state={"status": "draft", "solver_status": result.status, "profit": plan.profit_score},
        )
        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        if close_db:
            db.close()


def validate_and_apply_override(
    db: Session,
    org_id: str,
    user_id: Optional[str],
    assignment_id: str,
    new_employee_id: str,
    new_hours: int,
    is_locked: bool = True,
) -> Dict[str, Any]:
    """Applies manual override, re-validates hard constraints, and re-scores."""
    asgn = db.query(Assignment).filter(Assignment.id == assignment_id, Assignment.org_id == org_id).first()
    if not asgn:
        raise ValueError("Assignment not found")

    new_emp = db.query(Employee).filter(Employee.id == new_employee_id, Employee.org_id == org_id).first()
    if not new_emp:
        raise ValueError("Assigned employee not found")

    role = asgn.project_role
    plan = asgn.plan

    # Hard Constraint Check 1: Zero hours on leave
    ref_start = plan.start_date
    for lv in new_emp.leaves:
        wk_start = ((lv.start_date - ref_start).days // 7) + 1
        wk_end = ((lv.end_date - ref_start).days // 7) + 1
        if wk_start <= asgn.week_number <= wk_end:
            raise ValueError(
                f"Hard Constraint Violation: {new_emp.name} is on approved leave ({lv.reason or 'PTO'}) "
                f"during week {asgn.week_number}."
            )

    # Hard Constraint Check 2: Skill Qualification & Stretch
    emp_input = EmployeeInput(
        id=new_emp.id,
        name=new_emp.name,
        role=new_emp.role,
        cost_per_hour=new_emp.cost_per_hour,
        skills={
            es.skill_id: EmployeeSkillProficiency(
                skill_id=es.skill_id,
                skill_name=es.skill.name,
                proficiency=es.proficiency,
                growth_target=es.growth_target,
            )
            for es in new_emp.skills
        },
    )
    role_input = ProjectRoleInput(
        id=role.id,
        project_id=role.project_id,
        role_title=role.role_title,
        hours_per_week=role.hours_per_week,
        start_week=asgn.week_number,
        end_week=asgn.week_number,
        is_stretch_allowed=role.is_stretch_allowed,
        required_skills=[
            SkillRequirement(
                skill_id=prs.skill_id,
                skill_name=prs.skill.name,
                min_proficiency=prs.min_proficiency,
            )
            for prs in role.skill_requirements
        ],
    )

    is_qualified = is_employee_qualified_for_role(emp_input, role_input, allow_stretch=role.is_stretch_allowed)
    if not is_qualified:
        req_str = ", ".join(f"{sr.skill_name} (Lvl {sr.min_proficiency})" for sr in role_input.required_skills)
        raise ValueError(
            f"Hard Constraint Violation: {new_emp.name} does not meet skill requirements ({req_str}) "
            f"for role '{role.role_title}'."
        )

    # Hard Constraint Check 3: Weekly Capacity
    other_assignments = (
        db.query(Assignment)
        .filter(
            Assignment.plan_id == plan.id,
            Assignment.employee_id == new_emp.id,
            Assignment.week_number == asgn.week_number,
            Assignment.id != asgn.id,
        )
        .all()
    )
    total_assigned = sum(oa.hours for oa in other_assignments) + new_hours
    max_cap = new_emp.weekly_capacity_hours + new_emp.max_overtime_hours
    if total_assigned > max_cap:
        raise ValueError(
            f"Hard Constraint Violation: Total weekly hours for {new_emp.name} ({total_assigned} hrs) "
            f"exceeds maximum capacity plus overtime ({max_cap} hrs)."
        )

    # Apply override
    before_state = {
        "employee_id": asgn.employee_id,
        "hours": asgn.hours,
        "is_locked": asgn.is_locked,
    }

    asgn.employee_id = new_emp.id
    asgn.hours = new_hours
    asgn.is_locked = is_locked
    asgn.reasons = {
        "manual_override": True,
        "modified_by_user": user_id,
        "skill_match": [sr.skill_name for sr in role_input.required_skills],
    }

    db.flush()

    # Re-calculate simple profit score delta
    cost_diff = (new_hours * new_emp.cost_per_hour) - (before_state["hours"] * (asgn.employee.cost_per_hour if asgn.employee else 0))
    if plan.profit_score is not None:
        plan.profit_score -= cost_diff

    db.commit()

    log_audit_event(
        db=db,
        org_id=org_id,
        user_id=user_id,
        action="override_assignment",
        entity_type="assignment",
        entity_id=asgn.id,
        before_state=before_state,
        after_state={"employee_id": asgn.employee_id, "hours": asgn.hours, "is_locked": asgn.is_locked},
    )
    db.commit()

    return {
        "assignment_id": asgn.id,
        "employee_id": asgn.employee_id,
        "hours": asgn.hours,
        "is_locked": asgn.is_locked,
        "re_score": {
            "profit_score": plan.profit_score,
        },
    }


def create_scenario_with_diff(
    db: Session,
    base_plan_id: str,
    org_id: str,
    user_id: Optional[str],
    name: str,
    description: Optional[str],
    modifications: Dict[str, Any],
) -> Scenario:
    """Generates a scenario (what-if) solve and computes diff against base plan."""
    base_plan = db.query(Plan).filter(Plan.id == base_plan_id, Plan.org_id == org_id).first()
    if not base_plan:
        raise ValueError("Base plan not found")

    # Load base problem
    base_cfg = OptimizationConfig(
        horizon_weeks=base_plan.horizon_weeks,
        profit_weight=modifications.get("profit_weight", base_plan.profit_weight),
        growth_weight=modifications.get("growth_weight", base_plan.growth_weight),
        balance_weight=modifications.get("balance_weight", base_plan.balance_weight),
        time_limit_seconds=15.0,
    )
    if "slider_value" in modifications:
        base_cfg = OptimizationConfig.from_slider(
            slider_value=float(modifications["slider_value"]),
            horizon_weeks=base_plan.horizon_weeks,
            time_limit_seconds=15.0,
        )

    prob = load_problem_for_org(db, org_id, base_cfg, planning_start_date=base_plan.start_date)

    # Apply Modifications:
    # 1. Remove employee for weeks
    if "remove_employee_id" in modifications:
        rem_id = modifications["remove_employee_id"]
        start_w = modifications.get("leave_start_week", 1)
        end_w = modifications.get("leave_end_week", prob.horizon_weeks)
        for e in prob.employees:
            if e.id == rem_id:
                for w in range(start_w, end_w + 1):
                    e.leave_weeks.add(w)

    # 2. Add custom project / change project priority
    if "add_project" in modifications:
        pass  # Extensions for custom scenario projects

    # Solve modified problem
    result = solve_resource_allocation(prob)

    # Create modified Plan
    mod_plan = Plan(
        org_id=org_id,
        name=f"Scenario: {name}",
        status=PlanStatus.DRAFT,
        horizon_weeks=prob.horizon_weeks,
        start_date=base_plan.start_date,
        profit_weight=base_cfg.profit_weight,
        growth_weight=base_cfg.growth_weight,
        balance_weight=base_cfg.balance_weight,
        total_score=result.objective_breakdown.total_score,
        profit_score=result.objective_breakdown.profit,
        growth_score=result.objective_breakdown.growth_score,
        balance_penalty=result.objective_breakdown.balance_penalty,
        solver_status=result.status,
        solver_gap=result.stats.optimality_gap,
        solver_wall_time_ms=result.stats.wall_time_ms,
        inputs_hash=result.stats.inputs_hash,
        objective_breakdown={
            "profit": result.objective_breakdown.profit,
            "revenue": result.objective_breakdown.revenue,
            "labor_cost": result.objective_breakdown.labor_cost,
            "growth_score": result.objective_breakdown.growth_score,
        },
        dropped_project_reasons=explain_dropped_projects(prob, result),
        created_by=user_id,
    )
    db.add(mod_plan)
    db.flush()

    # Save assignments for modified plan
    for asgn in result.assignments:
        db_asgn = Assignment(
            org_id=org_id,
            plan_id=mod_plan.id,
            employee_id=asgn.employee_id,
            project_role_id=asgn.role_id,
            week_number=asgn.week,
            hours=asgn.hours,
            is_stretch=asgn.is_stretch,
            mentor_id=asgn.mentor_id,
            is_locked=asgn.is_locked,
            reasons=asgn.reasons,
        )
        db.add(db_asgn)
    db.flush()

    # Compute Diff Summary
    profit_delta = (mod_plan.profit_score or 0.0) - (base_plan.profit_score or 0.0)
    growth_delta = (mod_plan.growth_score or 0.0) - (base_plan.growth_score or 0.0)

    base_assignments = db.query(Assignment).filter(Assignment.plan_id == base_plan.id).all()
    base_map = {(a.project_role_id, a.week_number): a.employee_id for a in base_assignments}
    mod_map = {(a.project_role_id, a.week_number): a.employee_id for a in mod_plan.assignments}

    reassignments_count = 0
    moves = []
    for (r_id, w), m_emp in mod_map.items():
        b_emp = base_map.get((r_id, w))
        if b_emp and b_emp != m_emp:
            reassignments_count += 1
            if len(moves) < 10:  # Sample top moves
                moves.append({"role_id": r_id, "week": w, "from_employee": b_emp, "to_employee": m_emp})

    diff_summary = {
        "profit_delta": round(profit_delta, 2),
        "growth_delta": round(growth_delta, 2),
        "reassignments_count": reassignments_count,
        "sample_moves": moves,
    }

    scenario = Scenario(
        org_id=org_id,
        base_plan_id=base_plan.id,
        modified_plan_id=mod_plan.id,
        name=name,
        description=description,
        modifications=modifications,
        diff_summary=diff_summary,
        created_by=user_id,
    )
    db.add(scenario)
    db.commit()

    log_audit_event(
        db=db,
        org_id=org_id,
        user_id=user_id,
        action="create_scenario",
        entity_type="scenario",
        entity_id=scenario.id,
        after_state=diff_summary,
    )
    db.commit()

    return scenario
