from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import TenantModel


class Skill(TenantModel):
    __tablename__ = "skills"

    name = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("org_id", "name", name="uq_skill_org_name"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="skills")
    employee_skills = relationship("EmployeeSkill", back_populates="skill", cascade="all, delete-orphan")
    role_requirements = relationship("ProjectRoleSkill", back_populates="skill", cascade="all, delete-orphan")


class EmployeeSkill(TenantModel):
    __tablename__ = "employee_skills"

    employee_id = Column(
        String(36),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id = Column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    proficiency = Column(Integer, nullable=False)  # 1 to 5
    growth_target = Column(Integer, nullable=True)  # 1 to 5 optional target level

    __table_args__ = (
        UniqueConstraint("org_id", "employee_id", "skill_id", name="uq_emp_skill"),
    )

    # Relationships
    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")
