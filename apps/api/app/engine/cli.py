"""Optimization Engine CLI Runner

Runs the CP-SAT optimization engine against seeded database or standalone data,
printing formatted solution metrics, objective breakdown, and assignments.

Usage:
    python -m app.engine.cli [--slider 0.3] [--time-limit 30] [--pareto]
"""

import argparse
import os
import sys
from typing import Dict, Set

# Ensure apps/api is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import SessionLocal
from app.engine.domain import (
    EmployeeInput,
    EmployeeSkillProficiency,
    OptimizationConfig,
    OptimizationProblem,
    ProjectInput,
    ProjectRoleInput,
    SkillRequirement,
)
from app.engine.explainer import explain_dropped_projects
from app.engine.pareto import run_pareto_sweep
from app.engine.solver import solve_resource_allocation
from app.models import (
    Employee,
    Organization,
    Project,
)


def load_problem_from_database(
    slider_value: float = 0.3,
    time_limit: float = 30.0,
    horizon_weeks: int = 12,
) -> OptimizationProblem:
    """Loads optimization inputs directly from database into pure typed dataclasses."""
    db = SessionLocal()
    try:
        org = db.query(Organization).first()
        if not org:
            raise RuntimeError("Database not seeded! Please run 'python -m app.scripts.seed' first.")

        # 1. Load Employees
        db_employees = db.query(Employee).filter(Employee.org_id == org.id, Employee.is_active).all()
        employees: list[EmployeeInput] = []

        for e in db_employees:
            # Skills map
            skills_dict: Dict[str, EmployeeSkillProficiency] = {}
            for es in e.skills:
                skills_dict[es.skill_id] = EmployeeSkillProficiency(
                    skill_id=es.skill_id,
                    skill_name=es.skill.name,
                    proficiency=es.proficiency,
                    growth_target=es.growth_target,
                )

            # Leaves in horizon
            leave_weeks: Set[int] = set()
            for lv in e.leaves:
                from datetime import date
                ref_start = date(2026, 11, 2)
                wk_start = ((lv.start_date - ref_start).days // 7) + 1
                wk_end = ((lv.end_date - ref_start).days // 7) + 1
                for w in range(max(1, wk_start), min(horizon_weeks + 1, wk_end + 1)):
                    leave_weeks.add(w)

            emp_input = EmployeeInput(
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
            employees.append(emp_input)

        # 2. Load Projects and Roles
        db_projects = db.query(Project).filter(Project.org_id == org.id).all()
        projects: list[ProjectInput] = []

        from datetime import date
        ref_start = date(2026, 11, 2)

        for p in db_projects:
            roles_input: list[ProjectRoleInput] = []
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

        config = OptimizationConfig.from_slider(
            slider_value=slider_value,
            time_limit_seconds=time_limit,
            horizon_weeks=horizon_weeks,
        )

        return OptimizationProblem(
            horizon_weeks=horizon_weeks,
            employees=employees,
            projects=projects,
            locked_assignments=[],
            config=config,
        )
    finally:
        db.close()


def print_solution_report(problem: OptimizationProblem):
    print("=" * 80)
    print(" ALLOCATE OPTIMIZATION ENGINE - SOLVER RUN")
    print("=" * 80)
    print(f"Horizon: {problem.horizon_weeks} weeks | Employees: {len(problem.employees)} | Candidate Projects: {len(problem.projects)}")
    print(f"Slider: Profit Weight = {problem.config.profit_weight:.2f} | Growth Weight = {problem.config.growth_weight:.2f}")

    # Solve
    result = solve_resource_allocation(problem)

    print("\n--- SOLVER STATUS & TELEMETRY ---")
    print(f"Status:            {result.status}")
    print(f"Runtime:           {result.stats.wall_time_ms:.1f} ms")
    print(f"Optimality Gap:    {result.stats.optimality_gap * 100:.2f}%")
    print(f"Variables:         {result.stats.num_variables}")
    print(f"Constraints:       {result.stats.num_constraints}")
    print(f"Inputs SHA-256:    {result.stats.inputs_hash[:16]}...")

    if result.status not in ("OPTIMAL", "FEASIBLE"):
        print("\n[!] Optimization resulted in no feasible solution.")
        if result.pre_solve and result.pre_solve.conflicts:
            print("Pre-solve conflicts detected:")
            for c in result.pre_solve.conflicts:
                print(f" - {c}")
        return

    bd = result.objective_breakdown
    print("\n--- OBJECTIVE SCORE BREAKDOWN ---")
    print(f"Composite Score:   {bd.total_score:,.2f}")
    print(f"Net Profit:        ${bd.profit:,.2f}")
    print(f"  - Revenue:       ${bd.revenue:,.2f}")
    print(f"  - Labor Cost:    ${bd.labor_cost:,.2f}")
    print(f"  - Overtime Cost: ${bd.overtime_cost:,.2f}")
    print(f"Growth Score:      {bd.growth_score:,.2f} pts")
    print(f"  - Skill Gap:     {bd.skill_gap_closure_score:,.2f} pts")
    print(f"  - Stretch Bonus: {bd.stretch_bonus:,.2f} pts")
    print(f"  - Mentor Bonus:  {bd.mentor_bonus:,.2f} pts")
    print(f"Balance Penalty:   {bd.balance_penalty:,.2f} pts")

    # Project Selection
    print("\n--- PROJECT SELECTION SUMMARY ---")
    selected = [p for p in result.selected_projects if p.is_selected]
    dropped = [p for p in result.selected_projects if not p.is_selected]

    print(f"Selected ({len(selected)} / {len(problem.projects)} projects):")
    for sp in selected:
        print(f"  [x] {sp.project_name:<34} Rev: ${sp.revenue:>9,.0f} | Margin: ${sp.margin:>9,.0f}")

    # Generate explanations for dropped projects
    dropped_explanations = explain_dropped_projects(problem, result)
    print(f"\nDropped ({len(dropped)} / {len(problem.projects)} projects):")
    for dp in dropped:
        reason = dropped_explanations.get(dp.project_id, dp.reason_if_dropped)
        print(f"  [ ] {dp.project_name:<34} Reason: {reason}")

    # Assignments Sample (first 15 assignments)
    stretch_assignments = [a for a in result.assignments if a.is_stretch]
    print("\n--- ASSIGNMENTS SUMMARY ---")
    print(f"Total Assignment Records: {len(result.assignments)}")
    print(f"Stretch Assignments:      {len(stretch_assignments)}")

    if stretch_assignments:
        print("\nStretch & Mentoring Pairings Sample:")
        for sa in stretch_assignments[:5]:
            print(f"  - Mentee: {sa.employee_name} -> Role: '{sa.role_title}' on '{sa.project_name}' (Week {sa.week})")
            print(f"    Mentor: {sa.mentor_name} | Target Skills: {', '.join(sa.reasons.get('target_skills_developed', []))}")

    print("\n" + "=" * 80)


def print_pareto_table(problem: OptimizationProblem):
    print("=" * 80)
    print(" PARETO TRADEOFF SWEEP (PROFIT VS. GROWTH)")
    print("=" * 80)
    curve = run_pareto_sweep(problem, steps=5)

    print(f"{'Slider':<8} | {'Profit Weight':<14} | {'Net Profit':<14} | {'Growth Score':<14} | {'Selected Projs':<15} | {'Stretch Roles'}")
    print("-" * 80)
    for pt in curve:
        print(f"{pt['slider_value']:<8.2f} | {pt['profit_weight']:<14.3f} | ${pt['profit']:<13,.0f} | {pt['growth_score']:<14.1f} | {pt['selected_projects_count']:>2} / {pt['total_projects_count']:<10} | {pt['stretch_assignments_count']}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Allocate Optimization Engine CLI")
    parser.add_argument("--slider", type=float, default=0.3, help="Profit vs. Growth slider (0.0 to 1.0, default 0.3)")
    parser.add_argument("--time-limit", type=float, default=30.0, help="Solver time limit in seconds (default 30)")
    parser.add_argument("--pareto", action="store_true", help="Run 5-point Pareto sweep and display tradeoff table")

    args = parser.parse_args()

    problem = load_problem_from_database(
        slider_value=args.slider,
        time_limit=args.time_limit,
    )

    if args.pareto:
        print_pareto_table(problem)
    else:
        print_solution_report(problem)


if __name__ == "__main__":
    main()
