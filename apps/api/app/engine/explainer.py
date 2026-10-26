"""Explainability Module for Allocate

Generates structured explanations for assignments and dropped projects
using mathematical solver telemetry and counterfactual re-solves without LLMs.
"""

from copy import deepcopy
from typing import Dict

from app.engine.domain import OptimizationProblem, OptimizationResult
from app.engine.pre_solve import is_employee_qualified_for_role


def explain_dropped_projects(
    problem: OptimizationProblem,
    result: OptimizationResult,
) -> Dict[str, str]:
    """Determines exact structured reason why each unselected project was dropped."""
    explanations: Dict[str, str] = {}

    unselected = [p for p in problem.projects if not any(
        sp.project_id == p.id and sp.is_selected for sp in result.selected_projects
    )]

    for proj in unselected:
        # Check 1: Inherent skill gap
        has_skill_gap = False
        missing_role = None
        for role in proj.roles:
            qualified = [
                e for e in problem.employees
                if is_employee_qualified_for_role(e, role, allow_stretch=role.is_stretch_allowed)
            ]
            if not qualified:
                has_skill_gap = True
                missing_role = role
                break

        if has_skill_gap and missing_role:
            req_str = ", ".join(f"{sr.skill_name} (Lvl {sr.min_proficiency})" for sr in missing_role.required_skills)
            explanations[proj.id] = (
                f"Skill gap: Organization lacks qualified personnel for role '{missing_role.role_title}' "
                f"requiring {req_str}."
            )
            continue

        # Check 2: Counterfactual force-selection solve to test capacity bottleneck
        counterfactual_prob = deepcopy(problem)
        # Fast 5-second check
        counterfactual_prob.config.time_limit_seconds = 5.0
        # Set target project mandatory
        for p in counterfactual_prob.projects:
            if p.id == proj.id:
                p.mandatory = True
                break

        from app.engine.solver import solve_resource_allocation
        cf_result = solve_resource_allocation(counterfactual_prob)

        if cf_result.status == "INFEASIBLE":
            explanations[proj.id] = (
                "Insufficient team capacity: Staffing this project conflicts with concurrent project caps, "
                "workload capacity, or scheduled employee leaves."
            )
        else:
            profit_diff = result.objective_breakdown.profit - cf_result.objective_breakdown.profit
            if profit_diff > 0:
                explanations[proj.id] = (
                    f"Displaced by higher-value portfolio: Selecting this project would displace "
                    f"${profit_diff:,.0f} in net portfolio profit."
                )
            else:
                explanations[proj.id] = (
                    "Displaced by alternative projects with superior strategic priority and growth contribution."
                )

    return explanations
