"""Pareto Tradeoff Sweep Generator

Runs solver across multiple slider weight settings (e.g. 5 points from 100% profit to 100% growth)
to construct the empirical Pareto frontier.
"""

from copy import deepcopy
from typing import Any, Dict, List

from app.engine.domain import OptimizationConfig, OptimizationProblem
from app.engine.solver import solve_resource_allocation


def run_pareto_sweep(problem: OptimizationProblem, steps: int = 5) -> List[Dict[str, Any]]:
    """Runs solver at 'steps' points from slider 0.0 to 1.0 and returns tradeoff curve."""
    curve: List[Dict[str, Any]] = []

    # Default 5 evenly spaced slider points
    slider_points = [i / (steps - 1) for i in range(steps)]

    for slider in slider_points:
        # Clone problem with updated slider weights
        prob_copy = deepcopy(problem)
        prob_copy.config = OptimizationConfig.from_slider(
            slider_value=slider,
            time_limit_seconds=min(prob_copy.config.time_limit_seconds, 15.0),  # Fast solves for sweep
            random_seed=prob_copy.config.random_seed,
            max_concurrent_projects=prob_copy.config.max_concurrent_projects,
            min_block_hours=prob_copy.config.min_block_hours,
            mentor_time_ratio=prob_copy.config.mentor_time_ratio,
            overtime_penalty_per_hour=prob_copy.config.overtime_penalty_per_hour,
        )

        result = solve_resource_allocation(prob_copy)

        selected_count = sum(1 for p in result.selected_projects if p.is_selected)
        stretch_count = sum(1 for a in result.assignments if a.is_stretch)

        point = {
            "slider_value": round(slider, 2),
            "profit_weight": round(prob_copy.config.profit_weight, 3),
            "growth_weight": round(prob_copy.config.growth_weight, 3),
            "profit": round(result.objective_breakdown.profit, 2),
            "growth_score": round(result.objective_breakdown.growth_score, 2),
            "revenue": round(result.objective_breakdown.revenue, 2),
            "labor_cost": round(result.objective_breakdown.labor_cost, 2),
            "overtime_cost": round(result.objective_breakdown.overtime_cost, 2),
            "selected_projects_count": selected_count,
            "total_projects_count": len(prob_copy.projects),
            "stretch_assignments_count": stretch_count,
            "status": result.status,
            "optimality_gap": round(result.stats.optimality_gap, 4),
        }
        curve.append(point)

    return curve
