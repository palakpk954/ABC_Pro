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
