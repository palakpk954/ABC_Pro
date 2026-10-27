from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LockedAssignmentSchema(BaseModel):
    employee_id: str
    project_role_id: str
    week: int
    hours: int


class PlanGenerateRequest(BaseModel):
    name: Optional[str] = "Staffing Plan"
    start_date: Optional[date] = None
    horizon_weeks: int = Field(default=12, ge=1, le=52)
    profit_weight: float = Field(default=0.6, ge=0.0, le=1.0)
    growth_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    balance_weight: float = Field(default=0.1, ge=0.0, le=1.0)
    slider_value: Optional[float] = Field(None, ge=0.0, le=1.0)
    time_limit_seconds: float = Field(default=30.0, ge=1.0, le=300.0)
    locked_assignments: List[LockedAssignmentSchema] = Field(default_factory=list)


class AssignmentResponse(BaseModel):
    id: str
    plan_id: str
    employee_id: str
    employee_name: Optional[str] = None
    employee_role: Optional[str] = None
    project_role_id: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    role_title: Optional[str] = None
    week_number: int
    hours: int
    is_stretch: bool
    mentor_id: Optional[str] = None
    mentor_name: Optional[str] = None
    is_locked: bool
    reasons: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class PlanSummaryResponse(BaseModel):
    id: str
    org_id: str
    name: str
    status: str
    horizon_weeks: int
    start_date: date
    profit_weight: float
    growth_weight: float
    balance_weight: float
    total_score: Optional[float] = None
    profit_score: Optional[float] = None
    growth_score: Optional[float] = None
    balance_penalty: Optional[float] = None
    solver_status: Optional[str] = None
    solver_gap: Optional[float] = None
    solver_wall_time_ms: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlanDetailResponse(PlanSummaryResponse):
    objective_breakdown: Optional[Dict[str, Any]] = None
    dropped_project_reasons: Optional[Dict[str, Any]] = None
    assignments: List[AssignmentResponse] = Field(default_factory=list)
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class ParetoPointResponse(BaseModel):
    slider_value: float
    profit_weight: float
    growth_weight: float
    profit: float
    growth_score: float
    revenue: float
    labor_cost: float
    overtime_cost: float
    selected_projects_count: int
    total_projects_count: int
    stretch_assignments_count: int
    status: str
    optimality_gap: float


class ParetoSweepResponse(BaseModel):
    plan_id: Optional[str] = None
    points: List[ParetoPointResponse]


class AssignmentOverrideItem(BaseModel):
    employee_id: str
    project_role_id: str
    week_number: int
    hours: int
    is_locked: bool = True


class AssignmentOverrideRequest(BaseModel):
    overrides: List[AssignmentOverrideItem]


class PlanStatusUpdateRequest(BaseModel):
    status: str  # approved, rejected, draft
    comment: Optional[str] = None
