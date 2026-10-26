"""Pre-solve Feasibility Check & Conflict Reporter

Analyzes optimization inputs prior to solver execution to identify obvious
unresolvable bottlenecks or inconsistencies in plain English.
"""

from typing import Dict, List

from app.engine.domain import (
    EmployeeInput,
    OptimizationProblem,
    PreSolveDiagnostic,
    ProjectRoleInput,
)


def is_employee_qualified_for_role(
    emp: EmployeeInput,
    role: ProjectRoleInput,
    allow_stretch: bool = False,
) -> bool:
    """Checks whether an employee satisfies all required skills for a role."""
    for req in role.required_skills:
        emp_skill = emp.skills.get(req.skill_id)
        current_prof = emp_skill.proficiency if emp_skill else 0
        
        if allow_stretch and role.is_stretch_allowed:
            # Stretch qualification: proficiency >= required - 1
            if current_prof < req.min_proficiency - 1:
                return False
        else:
            if current_prof < req.min_proficiency:
                return False
    return True


def is_employee_stretch(emp: EmployeeInput, role: ProjectRoleInput) -> bool:
    """Returns True if employee qualifies only via stretch (i.e. at least one skill is required - 1)."""
    if not role.is_stretch_allowed:
        return False
    
    is_fully_qualified = True
    can_stretch = True
    
    for req in role.required_skills:
        emp_skill = emp.skills.get(req.skill_id)
        current_prof = emp_skill.proficiency if emp_skill else 0
        if current_prof < req.min_proficiency:
            is_fully_qualified = False
        if current_prof < req.min_proficiency - 1:
            can_stretch = False

    return can_stretch and not is_fully_qualified


def run_pre_solve_check(problem: OptimizationProblem) -> PreSolveDiagnostic:
    conflicts: List[str] = []
    warnings: List[str] = []

    emp_map: Dict[str, EmployeeInput] = {e.id: e for e in problem.employees}

    # 1. Check Mandatory Project Role Eligibility & Mentorship
    for proj in problem.projects:
        for role in proj.roles:
            # Find eligible employees
            standard_qualified = [
                e for e in problem.employees
                if is_employee_qualified_for_role(e, role, allow_stretch=False)
            ]
            stretch_qualified = [
                e for e in problem.employees
                if is_employee_stretch(e, role)
            ]

            total_qualified = len(standard_qualified) + len(stretch_qualified)

            if total_qualified == 0:
                skill_reqs_str = ", ".join(
                    f"{sr.skill_name} (Lvl {sr.min_proficiency})"
                    for sr in role.required_skills
                )
                msg = (
                    f"Role '{role.role_title}' in project '{proj.name}' requires {skill_reqs_str}, "
                    f"but no employee in the organization meets this criteria"
                    f"{' (even with stretch)' if role.is_stretch_allowed else ''}."
                )
                if proj.mandatory:
                    conflicts.append(f"MANDATORY CONFLICT: {msg}")
                else:
                    warnings.append(f"Project '{proj.name}' cannot be staffed: {msg}")

            elif proj.mandatory and len(standard_qualified) == 0 and len(stretch_qualified) > 0:
                # Role requires stretch, ensure there is at least one potential mentor in the org
                potential_mentors = [
                    e for e in problem.employees
                    if is_employee_qualified_for_role(e, role, allow_stretch=False)
                ]
                if not potential_mentors:
                    conflicts.append(
                        f"MANDATORY CONFLICT: Role '{role.role_title}' in '{proj.name}' can only be filled "
                        f"as a stretch role, but there is no qualified mentor with required proficiency."
                    )

    # 2. Check Weekly Mandatory Hours vs. Total Available Capacity
    for week in range(1, problem.horizon_weeks + 1):
        mandatory_hours_demanded = 0
        for proj in problem.projects:
            if proj.mandatory:
                for role in proj.roles:
                    if role.start_week <= week <= role.end_week:
                        mandatory_hours_demanded += role.hours_per_week

        total_available_capacity = sum(
            e.weekly_capacity_hours + e.max_overtime_hours
            for e in problem.employees
            if week not in e.leave_weeks
        )

        if mandatory_hours_demanded > total_available_capacity:
            conflicts.append(
                f"MANDATORY CONFLICT in Week {week}: Mandatory projects demand {mandatory_hours_demanded} hours, "
                f"but total organization capacity (including overtime and accounting for leaves) is only {total_available_capacity} hours."
            )

    # 3. Check Locked Assignments
    for lock in problem.locked_assignments:
        emp = emp_map.get(lock.employee_id)
        if not emp:
            conflicts.append(f"Locked assignment references unknown employee ID '{lock.employee_id}'.")
            continue

        if lock.week in emp.leave_weeks:
            conflicts.append(
                f"Locked assignment for {emp.name} in week {lock.week} conflicts with approved leave."
            )

        # Check qualification for role
        target_role = None
        for p in problem.projects:
            for r in p.roles:
                if r.id == lock.project_role_id:
                    target_role = r
                    break
            if target_role:
                break

        if target_role and not is_employee_qualified_for_role(emp, target_role, allow_stretch=target_role.is_stretch_allowed):
            conflicts.append(
                f"Locked assignment for {emp.name} on role '{target_role.role_title}' violates skill requirements."
            )

    is_feasible = len(conflicts) == 0
    return PreSolveDiagnostic(is_feasible=is_feasible, conflicts=conflicts, warnings=warnings)
