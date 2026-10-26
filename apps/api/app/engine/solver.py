"""Google OR-Tools CP-SAT Optimization Engine for Allocate

Pure Python module with typed dataclasses, implementing:
- Project selection (portfolio optimization)
- Hard constraints (capacity, leaves, full role staffing, mandatory selection, max 2 concurrent projects, stretch mentorship)
- Tunable multi-objective (Profit, Growth Score, Workload Balance)
- Reproducible random seed, inputs hash, solver stats, and optimality gap.
"""

import time
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model

from app.engine.domain import (
    AssignmentResult,
    ObjectiveBreakdown,
    OptimizationProblem,
    OptimizationResult,
    ProjectSelectionResult,
    SolverStats,
)
from app.engine.pre_solve import (
    is_employee_qualified_for_role,
    is_employee_stretch,
    run_pre_solve_check,
)


def solve_resource_allocation(problem: OptimizationProblem) -> OptimizationResult:
    start_time = time.perf_counter()
    inputs_hash = problem.compute_inputs_hash()

    # 1. Run Pre-solve Feasibility Check
    pre_solve_diag = run_pre_solve_check(problem)
    if not pre_solve_diag.is_feasible:
        wall_time_ms = (time.perf_counter() - start_time) * 1000.0
        return OptimizationResult(
            status="INFEASIBLE",
            stats=SolverStats(
                status="INFEASIBLE",
                wall_time_ms=wall_time_ms,
                optimality_gap=1.0,
                num_variables=0,
                num_constraints=0,
                inputs_hash=inputs_hash,
            ),
            objective_breakdown=ObjectiveBreakdown(
                total_score=0.0,
                profit=0.0,
                revenue=0.0,
                labor_cost=0.0,
                overtime_cost=0.0,
                growth_score=0.0,
                skill_gap_closure_score=0.0,
                stretch_bonus=0.0,
                mentor_bonus=0.0,
                balance_penalty=0.0,
                utilization_variance=0.0,
                overutilization_penalty=0.0,
            ),
            selected_projects=[],
            assignments=[],
            pre_solve=pre_solve_diag,
        )

    model = cp_model.CpModel()
    cfg = problem.config
    horizon = problem.horizon_weeks

    # Data structures for indexing
    emp_map = {e.id: e for e in problem.employees}

    # ---------------------------------------------------------
    # Decision Variables
    # ---------------------------------------------------------
    # y[p] in {0, 1}: project selection
    y: Dict[str, cp_model.IntVar] = {}
    for p in problem.projects:
        y[p.id] = model.NewBoolVar(f"y_{p.id}")
        if p.mandatory:
            # HC-3: Mandatory projects must be selected
            model.Add(y[p.id] == 1)

    # a[e, r] in {0, 1}: employee e is staffed on role r
    # is_stretch[e, r] in {0, 1}: stretch assignment flag
    # x[e, r, w] in [0, 40]: hours assigned
    a: Dict[Tuple[str, str], cp_model.IntVar] = {}
    is_stretch: Dict[Tuple[str, str], cp_model.IntVar] = {}
    x: Dict[Tuple[str, str, int], cp_model.IntVar] = {}

    # Precompute eligibility
    eligible_employees: Dict[str, List[str]] = {}  # role_id -> list of eligible emp_ids
    stretch_employees: Dict[str, List[str]] = {}   # role_id -> list of stretch-only emp_ids
    fully_qualified_employees: Dict[str, List[str]] = {}

    for p in problem.projects:
        for r in p.roles:
            eligible_employees[r.id] = []
            stretch_employees[r.id] = []
            fully_qualified_employees[r.id] = []

            for e in problem.employees:
                if is_employee_qualified_for_role(e, r, allow_stretch=False):
                    fully_qualified_employees[r.id].append(e.id)
                    eligible_employees[r.id].append(e.id)
                elif r.is_stretch_allowed and is_employee_stretch(e, r):
                    stretch_employees[r.id].append(e.id)
                    eligible_employees[r.id].append(e.id)

            for e_id in eligible_employees[r.id]:
                a[(e_id, r.id)] = model.NewBoolVar(f"a_{e_id}_{r.id}")
                is_stretch[(e_id, r.id)] = model.NewBoolVar(f"stretch_{e_id}_{r.id}")

                if e_id in stretch_employees[r.id]:
                    # Must be stretch if staffed
                    model.Add(is_stretch[(e_id, r.id)] == a[(e_id, r.id)])
                else:
                    # Fully qualified: not a stretch
                    model.Add(is_stretch[(e_id, r.id)] == 0)

                for w in range(1, horizon + 1):
                    if r.start_week <= w <= r.end_week:
                        x[(e_id, r.id, w)] = model.NewIntVar(0, r.hours_per_week, f"x_{e_id}_{r.id}_{w}")
                    else:
                        x[(e_id, r.id, w)] = model.NewConstant(0)

    # Overtime variables: overtime[e, w]
    overtime: Dict[Tuple[str, int], cp_model.IntVar] = {}
    for e in problem.employees:
        for w in range(1, horizon + 1):
            if w in e.leave_weeks:
                overtime[(e.id, w)] = model.NewConstant(0)
            else:
                overtime[(e.id, w)] = model.NewIntVar(0, e.max_overtime_hours, f"ot_{e.id}_{w}")

    # Mentorship variables: mentor[m, e, r] in {0, 1}
    # m is mentor for stretch employee e on role r of project p
    mentor_vars: Dict[Tuple[str, str, str], cp_model.IntVar] = {}
    for p in problem.projects:
        for r in p.roles:
            if r.is_stretch_allowed and stretch_employees[r.id]:
                # Potential mentors: fully qualified for role r
                qualified_mentors = fully_qualified_employees[r.id]
                for mentee_id in stretch_employees[r.id]:
                    for m_id in qualified_mentors:
                        if m_id != mentee_id:
                            mentor_vars[(m_id, mentee_id, r.id)] = model.NewBoolVar(f"mentor_{m_id}_{mentee_id}_{r.id}")

    # ---------------------------------------------------------
    # Hard Constraints
    # ---------------------------------------------------------

    # HC-2: Role Demand Coverage & Project Selection
    for p in problem.projects:
        for r in p.roles:
            for w in range(1, horizon + 1):
                if r.start_week <= w <= r.end_week:
                    eligible_for_role = eligible_employees[r.id]
                    if eligible_for_role:
                        model.Add(
                            sum(x[(e_id, r.id, w)] for e_id in eligible_for_role) == r.hours_per_week * y[p.id]
                        )
                    else:
                        # Cannot select project if no one is eligible for a role
                        model.Add(y[p.id] == 0)

            # Link x[e, r, w] and a[e, r]: Block size and assignment indicator
            for e_id in eligible_employees[r.id]:
                active_weeks = [w for w in range(1, horizon + 1) if r.start_week <= w <= r.end_week]
                if active_weeks:
                    for w in active_weeks:
                        # Upper bound: x <= hours * a
                        model.Add(x[(e_id, r.id, w)] <= r.hours_per_week * a[(e_id, r.id)])
                        # Minimum block size when assigned (e.g. 10 hours)
                        min_block = min(cfg.min_block_hours, r.hours_per_week)
                        # If a is 1, total hours across project must be at least min_block
                    model.Add(sum(x[(e_id, r.id, w)] for w in active_weeks) >= min_block * a[(e_id, r.id)])

    # HC-5: Stretch Mentorship Requirement
    for p in problem.projects:
        for r in p.roles:
            if r.is_stretch_allowed and stretch_employees[r.id]:
                qualified_mentors = fully_qualified_employees[r.id]
                for mentee_id in stretch_employees[r.id]:
                    relevant_mentor_vars = [
                        mentor_vars[(m_id, mentee_id, r.id)]
                        for m_id in qualified_mentors
                        if (m_id, mentee_id, r.id) in mentor_vars
                    ]
                    if relevant_mentor_vars:
                        # Exactly one mentor required if mentee is staffed on stretch role
                        model.Add(sum(relevant_mentor_vars) == is_stretch[(mentee_id, r.id)])
                        for m_id in qualified_mentors:
                            if (m_id, mentee_id, r.id) in mentor_vars:
                                # Mentor m must also be staffed on a role in the same project p
                                mentor_roles_on_proj = [
                                    a[(m_id, r_prime.id)]
                                    for r_prime in p.roles
                                    if (m_id, r_prime.id) in a
                                ]
                                if mentor_roles_on_proj:
                                    model.Add(mentor_vars[(m_id, mentee_id, r.id)] <= sum(mentor_roles_on_proj))
                                else:
                                    model.Add(mentor_vars[(m_id, mentee_id, r.id)] == 0)
                    else:
                        # No qualified mentor available, mentee cannot stretch
                        model.Add(is_stretch[(mentee_id, r.id)] == 0)

    # HC-1: Weekly Capacity, Leave, and Mentoring Load
    for e in problem.employees:
        for w in range(1, horizon + 1):
            if w in e.leave_weeks:
                # Strictly 0 hours during leave
                assigned_in_week = [
                    x[(e.id, r.id, w)]
                    for p in problem.projects
                    for r in p.roles
                    if (e.id, r.id, w) in x
                ]
                if assigned_in_week:
                    model.Add(sum(assigned_in_week) == 0)
                model.Add(overtime[(e.id, w)] == 0)
            else:
                # Regular working hours
                assigned_in_week = [
                    x[(e.id, r.id, w)]
                    for p in problem.projects
                    for r in p.roles
                    if (e.id, r.id, w) in x
                ]
                # Mentoring hours incurred by e in week w
                mentoring_hours_list = []
                for p in problem.projects:
                    for r in p.roles:
                        if r.start_week <= w <= r.end_week and r.is_stretch_allowed:
                            for mentee_id in stretch_employees.get(r.id, []):
                                if (e.id, mentee_id, r.id) in mentor_vars:
                                    mentor_load_hrs = int(round(cfg.mentor_time_ratio * r.hours_per_week))
                                    mentoring_hours_list.append(
                                        mentor_vars[(e.id, mentee_id, r.id)] * mentor_load_hrs
                                    )

                total_load = sum(assigned_in_week) + sum(mentoring_hours_list)
                model.Add(total_load <= e.weekly_capacity_hours + overtime[(e.id, w)])

    # HC-4: Max Concurrent Projects per Employee in each week (default 2)
    for e in problem.employees:
        for w in range(1, horizon + 1):
            if w not in e.leave_weeks:
                active_proj_vars = []
                for p in problem.projects:
                    proj_roles_week = [
                        x[(e.id, r.id, w)]
                        for r in p.roles
                        if (e.id, r.id, w) in x
                    ]
                    if proj_roles_week:
                        is_active_on_proj = model.NewBoolVar(f"active_{e.id}_{p.id}_{w}")
                        # If sum(x) > 0 => is_active_on_proj = 1
                        total_proj_demand = sum(r.hours_per_week for r in p.roles)
                        model.Add(sum(proj_roles_week) <= total_proj_demand * is_active_on_proj)
                        active_proj_vars.append(is_active_on_proj)

                if active_proj_vars:
                    model.Add(sum(active_proj_vars) <= cfg.max_concurrent_projects)

    # Honor Locked Assignments
    for lock in problem.locked_assignments:
        if (lock.employee_id, lock.project_role_id, lock.week) in x:
            model.Add(x[(lock.employee_id, lock.project_role_id, lock.week)] == lock.hours)

    # ---------------------------------------------------------
    # Multi-Objective Function Construction
    # ---------------------------------------------------------
    # Scale integer weights for exact arithmetic (SCALE = 100)
    SCALE = 100

    # 1. Profit Objective
    # Revenue ($) - Labor Cost ($) - Overtime Penalty ($)
    profit_terms = []
    for p in problem.projects:
        profit_terms.append(int(round(p.revenue * SCALE)) * y[p.id])

    for e in problem.employees:
        for p in problem.projects:
            for r in p.roles:
                for w in range(1, horizon + 1):
                    if (e.id, r.id, w) in x:
                        hourly_cost_scaled = int(round(e.cost_per_hour * SCALE))
                        profit_terms.append(-hourly_cost_scaled * x[(e.id, r.id, w)])

        for w in range(1, horizon + 1):
            ot_penalty_scaled = int(round(cfg.overtime_penalty_per_hour * SCALE))
            profit_terms.append(-ot_penalty_scaled * overtime[(e.id, w)])

    # 2. Growth Score Objective
    # Skill gap closure + stretch bonus + mentor bonus - repetition penalty
    growth_terms = []
    for p in problem.projects:
        for r in p.roles:
            for e_id in eligible_employees[r.id]:
                emp = emp_map[e_id]
                # Calculate skill-gap closure value
                gap_val = 0
                for req in r.required_skills:
                    emp_sk = emp.skills.get(req.skill_id)
                    cur_prof = emp_sk.proficiency if emp_sk else 0
                    growth_tgt = emp_sk.growth_target if emp_sk and emp_sk.growth_target else 0
                    if growth_tgt > cur_prof:
                        gap_val += (growth_tgt - cur_prof) * req.min_proficiency * 25
                    elif req.skill_name in emp.career_goals:
                        gap_val += req.min_proficiency * 20

                if gap_val > 0:
                    for w in range(1, horizon + 1):
                        if (e_id, r.id, w) in x:
                            growth_terms.append(gap_val * x[(e_id, r.id, w)])

                # Stretch bonus (e.g. 500 points * SCALE)
                if r.is_stretch_allowed and e_id in stretch_employees[r.id]:
                    stretch_bonus = 600 * SCALE
                    growth_terms.append(stretch_bonus * is_stretch[(e_id, r.id)])

                # Repetition penalty if fully overqualified (proficiency 5 in all skills, no growth target)
                is_overqualified = all(
                    emp.skills.get(req.skill_id) and emp.skills[req.skill_id].proficiency >= 5
                    for req in r.required_skills
                )
                if is_overqualified:
                    rep_penalty = 150 * SCALE
                    growth_terms.append(-rep_penalty * a[(e_id, r.id)])

    # Mentoring bonus for mentors
    for _key, m_var in mentor_vars.items():
        mentor_bonus = 400 * SCALE
        growth_terms.append(mentor_bonus * m_var)

    # 3. Workload Balance Penalty
    # Penalize overtime and over-utilization (>90% standard capacity = >36 hrs)
    balance_penalty_terms = []
    for e in problem.employees:
        for w in range(1, horizon + 1):
            if w not in e.leave_weeks:
                # Excess hours above 36
                excess_util = model.NewIntVar(0, e.weekly_capacity_hours + e.max_overtime_hours, f"excess_{e.id}_{w}")
                assigned_hours = [
                    x[(e.id, r.id, w)]
                    for p in problem.projects
                    for r in p.roles
                    if (e.id, r.id, w) in x
                ]
                model.Add(excess_util >= sum(assigned_hours) - 36)
                balance_penalty_terms.append(30 * SCALE * excess_util)

    # Composite Scalar Objective
    # Total = profit_weight * profit + growth_weight * growth - balance_weight * balance
    # All weights normalized and scaled
    pw_scaled = int(round(cfg.profit_weight * 1000))
    gw_scaled = int(round(cfg.growth_weight * 1000))
    bw_scaled = int(round(cfg.balance_weight * 1000))

    total_objective = (
        pw_scaled * sum(profit_terms) +
        gw_scaled * sum(growth_terms) -
        bw_scaled * sum(balance_penalty_terms)
    )
    model.Maximize(total_objective)

    # ---------------------------------------------------------
    # Solver Execution
    # ---------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = cfg.time_limit_seconds
    solver.parameters.random_seed = cfg.random_seed
    solver.parameters.num_workers = 4

    status_code = solver.Solve(model)
    wall_time_ms = (time.perf_counter() - start_time) * 1000.0

    status_str = {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.UNKNOWN: "UNKNOWN",
    }.get(status_code, "UNKNOWN")

    if status_code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return OptimizationResult(
            status=status_str,
            stats=SolverStats(
                status=status_str,
                wall_time_ms=wall_time_ms,
                optimality_gap=1.0,
                num_variables=len(model.Proto().variables),
                num_constraints=len(model.Proto().constraints),
                inputs_hash=inputs_hash,
            ),
            objective_breakdown=ObjectiveBreakdown(
                total_score=0.0,
                profit=0.0,
                revenue=0.0,
                labor_cost=0.0,
                overtime_cost=0.0,
                growth_score=0.0,
                skill_gap_closure_score=0.0,
                stretch_bonus=0.0,
                mentor_bonus=0.0,
                balance_penalty=0.0,
                utilization_variance=0.0,
                overutilization_penalty=0.0,
            ),
            selected_projects=[],
            assignments=[],
            pre_solve=pre_solve_diag,
        )

    # Calculate Optimality Gap
    best_bound = solver.BestObjectiveBound()
    objective_val = solver.ObjectiveValue()
    if abs(best_bound) > 1e-4:
        gap = abs(best_bound - objective_val) / abs(best_bound)
    else:
        gap = 0.0

    # ---------------------------------------------------------
    # Extract Solution & Compute Breakdown
    # ---------------------------------------------------------
    total_rev = 0.0
    total_labor = 0.0
    total_ot_cost = 0.0

    selected_projects_result: List[ProjectSelectionResult] = []
    for p in problem.projects:
        is_sel = bool(solver.Value(y[p.id]) == 1)
        proj_labor = 0.0
        if is_sel:
            total_rev += p.revenue
            for r in p.roles:
                for w in range(1, horizon + 1):
                    for e_id in eligible_employees[r.id]:
                        hrs = solver.Value(x[(e_id, r.id, w)])
                        if hrs > 0:
                            cost = hrs * emp_map[e_id].cost_per_hour
                            proj_labor += cost
            total_labor += proj_labor

        selected_projects_result.append(
            ProjectSelectionResult(
                project_id=p.id,
                project_name=p.name,
                is_selected=is_sel,
                revenue=p.revenue if is_sel else 0.0,
                labor_cost=proj_labor,
                margin=p.revenue - proj_labor if is_sel else 0.0,
                reason_if_dropped=None if is_sel else "Dropped due to capacity or lower composite value",
            )
        )

    for e in problem.employees:
        for w in range(1, horizon + 1):
            ot_hrs = solver.Value(overtime[(e.id, w)])
            total_ot_cost += ot_hrs * cfg.overtime_penalty_per_hour

    realized_profit = total_rev - total_labor - total_ot_cost

    # Extract Assignments and Structured Reasons
    assignments_result: List[AssignmentResult] = []
    skill_gap_total = 0.0
    stretch_bonus_total = 0.0
    mentor_bonus_total = 0.0

    for p in problem.projects:
        if solver.Value(y[p.id]) == 1:
            for r in p.roles:
                for w in range(1, horizon + 1):
                    for e_id in eligible_employees[r.id]:
                        hrs = solver.Value(x[(e_id, r.id, w)])
                        if hrs > 0:
                            emp = emp_map[e_id]
                            is_str = bool(solver.Value(is_stretch[(e_id, r.id)]) == 1)
                            
                            # Find mentor if stretch
                            matched_mentor_id = None
                            matched_mentor_name = None
                            if is_str:
                                for m_id in fully_qualified_employees[r.id]:
                                    if (m_id, e_id, r.id) in mentor_vars and solver.Value(mentor_vars[(m_id, e_id, r.id)]) == 1:
                                        matched_mentor_id = m_id
                                        matched_mentor_name = emp_map[m_id].name
                                        mentor_bonus_total += 400.0
                                        break
                                stretch_bonus_total += 600.0

                            # Growth value calculation
                            role_growth_val = 0.0
                            matched_skills = []
                            for req in r.required_skills:
                                emp_sk = emp.skills.get(req.skill_id)
                                cur_p = emp_sk.proficiency if emp_sk else 0
                                tgt_p = emp_sk.growth_target if emp_sk and emp_sk.growth_target else 0
                                if tgt_p > cur_p:
                                    role_growth_val += (tgt_p - cur_p) * req.min_proficiency * 25.0
                                    matched_skills.append(req.skill_name)
                                elif req.skill_name in emp.career_goals:
                                    role_growth_val += req.min_proficiency * 20.0
                                    matched_skills.append(req.skill_name)

                            skill_gap_total += (role_growth_val * hrs) / 40.0

                            # Explainability reasons
                            reasons = {
                                "skill_match": [sr.skill_name for sr in r.required_skills],
                                "cost_per_hour": emp.cost_per_hour,
                                "is_stretch": is_str,
                                "mentor": matched_mentor_name,
                                "target_skills_developed": matched_skills,
                                "growth_contribution": round(role_growth_val, 2),
                            }

                            assignments_result.append(
                                AssignmentResult(
                                    employee_id=emp.id,
                                    employee_name=emp.name,
                                    project_id=p.id,
                                    project_name=p.name,
                                    role_id=r.id,
                                    role_title=r.role_title,
                                    week=w,
                                    hours=hrs,
                                    is_stretch=is_str,
                                    mentor_id=matched_mentor_id,
                                    mentor_name=matched_mentor_name,
                                    is_locked=any(
                                        lock.employee_id == emp.id and lock.project_role_id == r.id and lock.week == w
                                        for lock in problem.locked_assignments
                                    ),
                                    reasons=reasons,
                                )
                            )

    growth_score_realized = skill_gap_total + stretch_bonus_total + mentor_bonus_total
    balance_penalty_realized = (total_ot_cost * 0.5)

    stats = SolverStats(
        status=status_str,
        wall_time_ms=wall_time_ms,
        optimality_gap=gap,
        num_variables=len(model.Proto().variables),
        num_constraints=len(model.Proto().constraints),
        inputs_hash=inputs_hash,
    )

    breakdown = ObjectiveBreakdown(
        total_score=objective_val / (SCALE * 1000.0),
        profit=realized_profit,
        revenue=total_rev,
        labor_cost=total_labor,
        overtime_cost=total_ot_cost,
        growth_score=growth_score_realized,
        skill_gap_closure_score=skill_gap_total,
        stretch_bonus=stretch_bonus_total,
        mentor_bonus=mentor_bonus_total,
        balance_penalty=balance_penalty_realized,
        utilization_variance=0.0,
        overutilization_penalty=0.0,
    )

    return OptimizationResult(
        status=status_str,
        stats=stats,
        objective_breakdown=breakdown,
        selected_projects=selected_projects_result,
        assignments=assignments_result,
        pre_solve=pre_solve_diag,
    )
