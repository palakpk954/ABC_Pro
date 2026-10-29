from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


class LockedAssignmentSchema(BaseModel):
    employee_id: str
    project_role_id: str
    week: int = Field(..., ge=1, le=52)
    hours: int = Field(..., ge=1, le=80)


class PlanGenerateRequest(BaseModel):
    name: Optional[str] = "Staffing Plan"
    horizon_weeks: int = Field(default=12, ge=1, le=52)
    start_date: Optional[date] = None
    slider_value: Optional[float] = Field(None, ge=0.0, le=1.0)
    profit_weight: Optional[float] = Field(0.6, ge=0.0, le=1.0)
    growth_weight: Optional[float] = Field(0.3, ge=0.0, le=1.0)
    balance_weight: Optional[float] = Field(0.1, ge=0.0, le=1.0)
    solver_time_limit_seconds: float = Field(default=30.0, ge=1.0, le=120.0)
    locked_assignments: List[LockedAssignmentSchema] = Field(default_factory=list)


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: str
    employee_name: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_role_id: str
    role_title: Optional[str] = None
    week_number: int
    hours: int
    is_stretch: bool
    mentor_id: Optional[str] = None
    mentor_name: Optional[str] = None
    is_locked: bool
    reasons: Optional[Dict[str, Any]] = None


class AssignmentOverrideRequest(BaseModel):
    assignment_id: str
    employee_id: str
    hours: int = Field(..., ge=0, le=80)
    is_locked: bool = True


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    inputs_hash: Optional[str] = None
    objective_breakdown: Optional[Dict[str, Any]] = None
    dropped_project_reasons: Optional[Dict[str, str]] = None
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    assignments: List[AssignmentResponse] = Field(default_factory=list)


class ScenarioCreateRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    modifications: Dict[str, Any] = Field(default_factory=dict)


class ScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    base_plan_id: str
    modified_plan_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    modifications: Dict[str, Any]
    diff_summary: Optional[Dict[str, Any]] = None
    created_at: datetime


class ParetoPoint(BaseModel):
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


class ParetoResponse(BaseModel):
    plan_id: str
    curve: List[ParetoPoint]
