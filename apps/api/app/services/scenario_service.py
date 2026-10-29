from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.plan import Assignment, Plan, Scenario
from app.schemas.plan import PlanGenerateRequest
from app.schemas.scenario import ScenarioCreateRequest
from app.services.audit_service import log_audit
from app.services.plan_service import build_optimization_problem_from_db


def create_and_run_scenario(
    org_id: str,
    db: Session,
    req: ScenarioCreateRequest,
    user_id: Optional[str] = None,
) -> Scenario:
    """Generates a what-if scenario, re-running the optimization engine with modified inputs
    and computing side-by-side metric and assignment diffs.
    """
    base_plan = (
        db.query(Plan)
        .options(joinedload(Plan.assignments))
        .filter(Plan.id == req.base_plan_id, Plan.org_id == org_id)
        .first()
    )
    if not base_plan:
        raise ValueError(f"Base plan {req.base_plan_id} not found")

    mods = req.modifications

    # Build generate request copying base plan's parameters with modifications
    gen_req = PlanGenerateRequest(
        name=f"Scenario: {req.name}",
        start_date=base_plan.start_date,
        horizon_weeks=base_plan.horizon_weeks,
        profit_weight=mods.profit_weight if mods.profit_weight is not None else base_plan.profit_weight,
        growth_weight=mods.growth_weight if mods.growth_weight is not None else base_plan.growth_weight,
        balance_weight=mods.balance_weight if mods.balance_weight is not None else base_plan.balance_weight,
        time_limit_seconds=15.0,
    )

    # Build problem and apply modifications in-memory
    problem = build_optimization_problem_from_db(
        org_id=org_id,
        db=db,
        req=gen_req,
        plan_start_date=base_plan.start_date,
    )

    # 1. Removed employees
    if mods.removed_employee_ids:
        problem.employees = [
            e for e in problem.employees if e.id not in mods.removed_employee_ids
        ]

    # 2. Added leave periods
    for item in mods.added_leave_periods:
        emp_id = item.get("employee_id")
        weeks = item.get("weeks", [])
        for e in problem.employees:
            if e.id == emp_id:
                for w in weeks:
                    e.leave_weeks.add(int(w))

    # 3. Removed projects
    if mods.removed_project_ids:
        problem.projects = [
            p for p in problem.projects if p.id not in mods.removed_project_ids
        ]

    # Solve modified problem
    import dataclasses

    from app.engine.explainer import explain_dropped_projects
    from app.engine.solver import solve_resource_allocation

    res = solve_resource_allocation(problem)
    dropped_reasons = explain_dropped_projects(problem, res)

    # Persist modified Plan
    from app.models.plan import PlanStatus
    mod_plan = Plan(
        org_id=org_id,
        name=f"Plan ({req.name})",
        status=PlanStatus.DRAFT,
        horizon_weeks=problem.horizon_weeks,
        start_date=base_plan.start_date,
        profit_weight=problem.config.profit_weight,
        growth_weight=problem.config.growth_weight,
        balance_weight=problem.config.balance_weight,
        total_score=res.objective_breakdown.total_score,
        profit_score=res.objective_breakdown.profit,
        growth_score=res.objective_breakdown.growth_score,
        balance_penalty=res.objective_breakdown.balance_penalty,
        solver_status=res.status,
        solver_gap=res.stats.optimality_gap,
        solver_wall_time_ms=res.stats.wall_time_ms,
        inputs_hash=res.stats.inputs_hash,
        objective_breakdown=dataclasses.asdict(res.objective_breakdown),
        dropped_project_reasons=dropped_reasons,
        created_by=user_id,
    )
    db.add(mod_plan)
    db.flush()

    # Persist modified Assignments
    for a in res.assignments:
        assign = Assignment(
            org_id=org_id,
            plan_id=mod_plan.id,
            employee_id=a.employee_id,
            project_role_id=a.role_id,
            week_number=a.week,
            hours=a.hours,
            is_stretch=a.is_stretch,
            mentor_id=a.mentor_id,
            is_locked=a.is_locked,
            reasons=a.reasons,
        )
        db.add(assign)

    # Calculate diff
    profit_delta = (mod_plan.profit_score or 0.0) - (base_plan.profit_score or 0.0)
    growth_delta = (mod_plan.growth_score or 0.0) - (base_plan.growth_score or 0.0)
    balance_delta = (mod_plan.balance_penalty or 0.0) - (base_plan.balance_penalty or 0.0)
    total_delta = (mod_plan.total_score or 0.0) - (base_plan.total_score or 0.0)

    base_proj_sel = set(base_plan.objective_breakdown.get("selected_project_ids", []) if base_plan.objective_breakdown else [])
    mod_proj_sel = set(sp.project_id for sp in res.selected_projects if sp.is_selected)

    added_projs = list(mod_proj_sel - base_proj_sel)
    removed_projs = list(base_proj_sel - mod_proj_sel)

    # Build assignment lookup
    base_assign_map = {
        (a.employee_id, a.project_role_id, a.week_number): a.hours
        for a in base_plan.assignments
    }
    mod_assign_map = {
        (a.employee_id, a.role_id, a.week): a.hours
        for a in res.assignments
    }

    all_keys = set(base_assign_map.keys()) | set(mod_assign_map.keys())
    assignments_diff = []
    for k in all_keys:
        b_hrs = base_assign_map.get(k, 0)
        m_hrs = mod_assign_map.get(k, 0)
        if b_hrs != m_hrs:
            assignments_diff.append({
                "employee_id": k[0],
                "project_role_id": k[1],
                "week_number": k[2],
                "base_hours": b_hrs,
                "scenario_hours": m_hrs,
                "delta": m_hrs - b_hrs,
            })

    diff_summary = {
        "profit_delta": round(profit_delta, 2),
        "growth_score_delta": round(growth_delta, 2),
        "balance_penalty_delta": round(balance_delta, 2),
        "total_score_delta": round(total_delta, 4),
        "selected_projects_added": added_projs,
        "selected_projects_removed": removed_projs,
        "assignments_changed_count": len(assignments_diff),
        "assignments_diff": assignments_diff[:100],  # cap first 100 for response size
    }

    scenario = Scenario(
        org_id=org_id,
        name=req.name,
        description=req.description,
        base_plan_id=base_plan.id,
        modified_plan_id=mod_plan.id,
        modifications=mods.model_dump(),
        diff_summary=diff_summary,
        created_by=user_id,
    )
    db.add(scenario)
    db.flush()

    log_audit(
        db=db,
        org_id=org_id,
        action="create_scenario",
        entity_type="scenario",
        entity_id=scenario.id,
        user_id=user_id,
        after_state={"name": req.name, "diff_summary": diff_summary},
    )

    db.commit()
    db.refresh(scenario)
    return scenario
