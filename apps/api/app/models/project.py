from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import TenantModel


class Project(TenantModel):
    __tablename__ = "projects"

    name = Column(String(255), nullable=False, index=True)
    client = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    revenue = Column(Float, nullable=False, default=0.0)  # total contract revenue / budget
    billing_rate_hourly = Column(Float, nullable=True)  # optional hourly billing rate
    priority = Column(Integer, nullable=False, default=3)  # 1 to 5
    mandatory = Column(Boolean, nullable=False, default=False)
    status = Column(String(50), nullable=False, default="proposed")  # proposed, active, completed, cancelled

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    roles = relationship("ProjectRole", back_populates="project", cascade="all, delete-orphan")


class ProjectRole(TenantModel):
    __tablename__ = "project_roles"

    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_title = Column(String(100), nullable=False)
    hours_per_week = Column(Integer, nullable=False, default=40)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_stretch_allowed = Column(Boolean, nullable=False, default=False)

    # Relationships
    project = relationship("Project", back_populates="roles")
    skill_requirements = relationship("ProjectRoleSkill", back_populates="project_role", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="project_role", cascade="all, delete-orphan")


class ProjectRoleSkill(TenantModel):
    __tablename__ = "project_role_skills"

    project_role_id = Column(
        String(36),
        ForeignKey("project_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id = Column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    min_proficiency = Column(Integer, nullable=False, default=3)  # 1 to 5

    __table_args__ = (
        UniqueConstraint("project_role_id", "skill_id", name="uq_role_skill"),
    )

    # Relationships
    project_role = relationship("ProjectRole", back_populates="skill_requirements")
    skill = relationship("Skill", back_populates="role_requirements")
