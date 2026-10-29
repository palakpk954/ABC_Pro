from typing import Optional, List
from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.schemas.skill import EmployeeSkillResponse


class EmployeeBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    role: str = Field(..., max_length=100)
    cost_per_hour: float = Field(..., gt=0)
    weekly_capacity_hours: int = Field(default=40, ge=1, le=80)
    max_overtime_hours: int = Field(default=10, ge=0, le=40)
    start_date: date
    end_date: Optional[date] = None
    career_goals: List[str] = Field(default_factory=list)
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, max_length=100)
    cost_per_hour: Optional[float] = Field(None, gt=0)
    weekly_capacity_hours: Optional[int] = Field(None, ge=1, le=80)
    max_overtime_hours: Optional[int] = Field(None, ge=0, le=40)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    career_goals: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EmployeeLeaveCreate(BaseModel):
    start_date: date
    end_date: date
    reason: Optional[str] = None


class EmployeeLeaveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: str
    start_date: date
    end_date: date
    reason: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    skills: List[EmployeeSkillResponse] = Field(default_factory=list)
    leaves: List[EmployeeLeaveResponse] = Field(default_factory=list)
