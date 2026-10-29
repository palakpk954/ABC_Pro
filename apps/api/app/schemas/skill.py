from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SkillBase(BaseModel):
    name: str = Field(..., max_length=100)
    category: str = Field(..., max_length=100)
    description: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class SkillResponse(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str


class EmployeeSkillCreate(BaseModel):
    skill_id: str
    proficiency: int = Field(..., ge=1, le=5)
    growth_target: Optional[int] = Field(None, ge=1, le=5)


class EmployeeSkillUpdate(BaseModel):
    proficiency: Optional[int] = Field(None, ge=1, le=5)
    growth_target: Optional[int] = Field(None, ge=1, le=5)


class EmployeeSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: str
    skill_id: str
    skill_name: Optional[str] = None
    skill_category: Optional[str] = None
    proficiency: int
    growth_target: Optional[int] = None
