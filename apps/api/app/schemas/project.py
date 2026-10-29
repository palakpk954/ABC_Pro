from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, ConfigDict


class ProjectRoleSkillCreate(BaseModel):
    skill_id: str
    min_proficiency: int = Field(..., ge=1, le=5)


class ProjectRoleSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_role_id: str
    skill_id: str
    skill_name: Optional[str] = None
    min_proficiency: int


class ProjectRoleBase(BaseModel):
    role_title: str = Field(..., max_length=100)
    hours_per_week: int = Field(default=40, ge=1, le=80)
    start_date: date
    end_date: date
    is_stretch_allowed: bool = False


class ProjectRoleCreate(ProjectRoleBase):
    skills: List[ProjectRoleSkillCreate] = Field(default_factory=list)


class ProjectRoleUpdate(BaseModel):
    role_title: Optional[str] = Field(None, max_length=100)
    hours_per_week: Optional[int] = Field(None, ge=1, le=80)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_stretch_allowed: Optional[bool] = None
    skills: Optional[List[ProjectRoleSkillCreate]] = None


class ProjectRoleResponse(ProjectRoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    skill_requirements: List[ProjectRoleSkillResponse] = Field(default_factory=list)


class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255)
    client: str = Field(..., max_length=255)
    start_date: date
    end_date: date
    revenue: float = Field(default=0.0, ge=0.0)
    billing_rate_hourly: Optional[float] = None
    priority: int = Field(default=3, ge=1, le=5)
    mandatory: bool = False
    status: str = Field(default="proposed", max_length=50)


class ProjectCreate(ProjectBase):
    roles: List[ProjectRoleCreate] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    client: Optional[str] = Field(None, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    revenue: Optional[float] = Field(None, ge=0.0)
    billing_rate_hourly: Optional[float] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    mandatory: Optional[bool] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    roles: List[ProjectRoleResponse] = Field(default_factory=list)
