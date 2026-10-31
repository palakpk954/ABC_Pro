from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ScenarioModificationSchema(BaseModel):
    # What-if adjustments
    removed_employee_ids: List[str] = Field(default_factory=list)
    added_leave_periods: List[Dict[str, Any]] = Field(default_factory=list)
    added_project_ids: List[str] = Field(default_factory=list)
    removed_project_ids: List[str] = Field(default_factory=list)
    profit_weight: Optional[float] = None
    growth_weight: Optional[float] = None
    balance_weight: Optional[float] = None


class ScenarioCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    base_plan_id: str
    modifications: ScenarioModificationSchema


class ScenarioDiffSummary(BaseModel):
    profit_delta: float
    growth_score_delta: float
    balance_penalty_delta: float
    total_score_delta: float
    selected_projects_added: List[str]
    selected_projects_removed: List[str]
    assignments_changed_count: int
    assignments_diff: List[Dict[str, Any]]


class ScenarioResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    base_plan_id: str
    modified_plan_id: Optional[str] = None
    modifications: Dict[str, Any]
    diff_summary: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ImpactedEngineerChange(BaseModel):
    employee_id: str
    employee_name: str
    role_title: str
    project_name: str
    previous_hours: int
    new_hours: int
    delta_hours: int
    change_type: str  # reallocated, reduced, backfilled, added
    rationale: str


class NaturalScenarioSimulateRequest(BaseModel):
    base_plan_id: str
    prompt: str


class NaturalScenarioSimulateResponse(BaseModel):
    scenario_name: str
    detected_perturbation: str
    executive_recommendation: str
    recommendation_verdict: str  # "Approved", "Caution", "Rejected"
    profit_delta: float
    growth_score_delta: float
    labor_cost_delta: float
    overtime_cost_delta: float
    feasibility_status: str
    assignments_shifted_count: int
    impacted_engineers: List[ImpactedEngineerChange] = Field(default_factory=list)
    suggested_mitigations: List[str] = Field(default_factory=list)

