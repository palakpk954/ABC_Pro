from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.skill import SkillResponse


class EmployeeSkillBase(BaseModel):
    skill_id: str
    proficiency: int = Field(..., ge=1, le=5)
    growth_target: Optional[int] = None


class EmployeeSkillCreate(EmployeeSkillBase):
    pass


class EmployeeSkillResponse(EmployeeSkillBase):
    id: str
    org_id: str
    employee_id: str
    skill: Optional[SkillResponse] = None

    class Config:
        from_attributes = True


class EmployeeLeaveBase(BaseModel):
    start_date: date
    end_date: date
    type: str = "vacation"  # vacation, sick, training, parental, other
    description: Optional[str] = None


class EmployeeLeaveCreate(EmployeeLeaveBase):
    pass


class EmployeeLeaveResponse(EmployeeLeaveBase):
    id: str
    org_id: str
    employee_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    role: str = Field(..., max_length=100)
    cost_per_hour: float = Field(..., gt=0)
    weekly_capacity_hours: int = Field(default=40, ge=1, le=80)
    max_overtime_hours: int = Field(default=10, ge=0, le=40)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    career_goals: List[str] = Field(default_factory=list)
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    skills: Optional[List[EmployeeSkillCreate]] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    cost_per_hour: Optional[float] = None
    weekly_capacity_hours: Optional[int] = None
    max_overtime_hours: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    career_goals: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: str
    org_id: str
    created_at: datetime
    updated_at: datetime
    skills: List[EmployeeSkillResponse] = Field(default_factory=list)
    leaves: List[EmployeeLeaveResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CandidateComparisonProfile(BaseModel):
    id: str
    name: str
    role: str
    hourly_rate: float
    archetype: str
    archetype_fit_rating: str  # High, Moderate, Neutral
    archetype_fit_score: int
    burnout_risk_score: float
    burnout_status: str
    coaching_sentiment: str
    stretch_readiness_score: float
    matching_skills: List[str] = Field(default_factory=list)
    evidence_quote: Optional[str] = None
    weekly_margin_generated: float


class CandidateMatchupResponse(BaseModel):
    role_title: str
    project_name: str
    candidate_a: CandidateComparisonProfile
    candidate_b: CandidateComparisonProfile
    recommended_candidate_id: str
    verdict_headline: str
    executive_counterfactual_explanation: str
    tradeoff_summary: Dict[str, Any]

