from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.skill import SkillResponse


class ProjectRoleSkillBase(BaseModel):
    skill_id: str
    min_proficiency: int = Field(default=3, ge=1, le=5)


class ProjectRoleSkillCreate(ProjectRoleSkillBase):
    pass


class ProjectRoleSkillResponse(ProjectRoleSkillBase):
    id: str
    org_id: str
    project_role_id: str
    skill: Optional[SkillResponse] = None

    class Config:
        from_attributes = True


class ProjectRoleBase(BaseModel):
    role_title: str = Field(..., max_length=100)
    hours_per_week: int = Field(default=40, ge=1, le=80)
    start_date: date
    end_date: date
    is_stretch_allowed: bool = False


class ProjectRoleCreate(ProjectRoleBase):
    skill_requirements: Optional[List[ProjectRoleSkillCreate]] = None


class ProjectRoleUpdate(BaseModel):
    role_title: Optional[str] = None
    hours_per_week: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_stretch_allowed: Optional[bool] = None


class ProjectRoleResponse(ProjectRoleBase):
    id: str
    org_id: str
    project_id: str
    created_at: datetime
    skill_requirements: List[ProjectRoleSkillResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255)
    client: str = Field(..., max_length=255)
    start_date: date
    end_date: date
    revenue: float = Field(default=0.0, ge=0.0)
    billing_rate_hourly: Optional[float] = None
    priority: int = Field(default=3, ge=1, le=5)
    mandatory: bool = False
    status: str = Field(default="proposed")  # proposed, active, completed, cancelled


class ProjectCreate(ProjectBase):
    roles: Optional[List[ProjectRoleCreate]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    revenue: Optional[float] = None
    billing_rate_hourly: Optional[float] = None
    priority: Optional[int] = None
    mandatory: Optional[bool] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    org_id: str
    created_at: datetime
    updated_at: datetime
    roles: List[ProjectRoleResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
