"""Domain Dataclasses for Allocate Optimization Engine

Pure Python typed dataclasses independent of database or web frameworks.
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass(frozen=True)
class SkillRequirement:
    skill_id: str
    skill_name: str
    min_proficiency: int  # 1 to 5


@dataclass(frozen=True)
class EmployeeSkillProficiency:
    skill_id: str
    skill_name: str
    proficiency: int  # 1 to 5
    growth_target: Optional[int] = None  # 1 to 5


@dataclass
class EmployeeInput:
    id: str
    name: str
    role: str
    cost_per_hour: float
    weekly_capacity_hours: int = 40
    max_overtime_hours: int = 10
    skills: Dict[str, EmployeeSkillProficiency] = field(default_factory=dict)
    leave_weeks: Set[int] = field(default_factory=set)  # 1-indexed week numbers
    career_goals: List[str] = field(default_factory=list)  # Target skill names
    archetype: str = "Generalist"  # Pathfinder, Optimizer, Firefighter, Mentor, Generalist
    burnout_risk_score: float = 0.15  # 0.0 (rested) to 1.0 (exhausted)
    coaching_sentiment: str = "Collaborative Contributor"
    stretch_readiness_score: float = 0.75
    career_aspirations: List[str] = field(default_factory=list)


@dataclass
class ProjectRoleInput:
    id: str
    project_id: str
    role_title: str
    hours_per_week: int
    start_week: int  # 1-indexed
    end_week: int    # 1-indexed, inclusive
    is_stretch_allowed: bool = False
    required_skills: List[SkillRequirement] = field(default_factory=list)


@dataclass
class ProjectInput:
    id: str
    name: str
    client: str
    start_week: int
    end_week: int
    revenue: float
    priority: int = 3  # 1 to 5
    mandatory: bool = False
    roles: List[ProjectRoleInput] = field(default_factory=list)
    archetype_focus: Optional[str] = None  # Pathfinder, Optimizer, Firefighter, Mentor, Generalist


@dataclass
class LockedAssignmentInput:
    employee_id: str
    project_role_id: str
    week: int
    hours: int


@dataclass
class OptimizationConfig:
    horizon_weeks: int = 12
    profit_weight: float = 0.6
    growth_weight: float = 0.3
    balance_weight: float = 0.1
    time_limit_seconds: float = 30.0
    random_seed: int = 42
    max_concurrent_projects: int = 2
    min_block_hours: int = 10
    mentor_time_ratio: float = 0.10
    overtime_penalty_per_hour: float = 50.0

    @classmethod
    def from_slider(cls, slider_value: float, **kwargs) -> "OptimizationConfig":
        """Maps single 0-1 slider: 0 = 100% Profit focus, 1 = 100% Growth focus."""
        s = max(0.0, min(1.0, slider_value))
        profit_w = (1.0 - s) * 0.85
        growth_w = s * 0.85
        balance_w = 0.15
        return cls(
            profit_weight=profit_w,
            growth_weight=growth_w,
            balance_weight=balance_w,
            **kwargs
        )


@dataclass
class OptimizationProblem:
    horizon_weeks: int
    employees: List[EmployeeInput]
    projects: List[ProjectInput]
    locked_assignments: List[LockedAssignmentInput] = field(default_factory=list)
    config: OptimizationConfig = field(default_factory=OptimizationConfig)

    def compute_inputs_hash(self) -> str:
        """Computes deterministic SHA-256 fingerprint of optimization input data."""
        data_rep = {
            "horizon": self.horizon_weeks,
            "employees": [
                {
                    "id": e.id,
                    "cost": e.cost_per_hour,
                    "cap": e.weekly_capacity_hours,
                    "ot": e.max_overtime_hours,
                    "leaves": sorted(list(e.leave_weeks)),
                    "skills": {s_id: (sp.proficiency, sp.growth_target) for s_id, sp in sorted(e.skills.items())},
                    "archetype": getattr(e, "archetype", "Generalist"),
                    "burnout": getattr(e, "burnout_risk_score", 0.15),
                }
                for e in sorted(self.employees, key=lambda x: x.id)
            ],
            "projects": [
                {
                    "id": p.id,
                    "rev": p.revenue,
                    "mand": p.mandatory,
                    "roles": [
                        {
                            "id": r.id,
                            "hrs": r.hours_per_week,
                            "wks": (r.start_week, r.end_week),
                            "stretch": r.is_stretch_allowed,
                            "skills": [(sr.skill_id, sr.min_proficiency) for sr in sorted(r.required_skills, key=lambda s: s.skill_id)],
                        }
                        for r in sorted(p.roles, key=lambda x: x.id)
                    ],
                }
                for p in sorted(self.projects, key=lambda x: x.id)
            ],
            "config": {
                "pw": self.config.profit_weight,
                "gw": self.config.growth_weight,
                "bw": self.config.balance_weight,
                "seed": self.config.random_seed,
            },
        }
        raw_json = json.dumps(data_rep, sort_keys=True)
        return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()


@dataclass
class AssignmentResult:
    employee_id: str
    employee_name: str
    project_id: str
    project_name: str
    role_id: str
    role_title: str
    week: int
    hours: int
    is_stretch: bool = False
    mentor_id: Optional[str] = None
    mentor_name: Optional[str] = None
    is_locked: bool = False
    reasons: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectSelectionResult:
    project_id: str
    project_name: str
    is_selected: bool
    revenue: float
    labor_cost: float
    margin: float
    reason_if_dropped: Optional[str] = None


@dataclass
class ObjectiveBreakdown:
    total_score: float
    profit: float
    revenue: float
    labor_cost: float
    overtime_cost: float
    growth_score: float
    skill_gap_closure_score: float
    stretch_bonus: float
    mentor_bonus: float
    balance_penalty: float
    utilization_variance: float
    overutilization_penalty: float
    archetype_synergy_score: float = 0.0
    burnout_fatigue_penalty: float = 0.0


@dataclass
class SolverStats:
    status: str  # OPTIMAL, FEASIBLE, INFEASIBLE, UNKNOWN
    wall_time_ms: float
    optimality_gap: float
    num_variables: int
    num_constraints: int
    inputs_hash: str


@dataclass
class PreSolveDiagnostic:
    is_feasible: bool
    conflicts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class OptimizationResult:
    status: str
    stats: SolverStats
    objective_breakdown: ObjectiveBreakdown
    selected_projects: List[ProjectSelectionResult]
    assignments: List[AssignmentResult]
    pre_solve: Optional[PreSolveDiagnostic] = None
