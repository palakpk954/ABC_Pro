from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import TenantModel


class Employee(TenantModel):
    __tablename__ = "employees"

    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False, index=True)  # e.g., Senior Backend Engineer
    cost_per_hour = Column(Float, nullable=False, default=75.0)
    weekly_capacity_hours = Column(Integer, nullable=False, default=40)
    max_overtime_hours = Column(Integer, nullable=False, default=10)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    career_goals = Column(JSON, nullable=False, default=list)  # list of target skill names or goals
    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("org_id", "email", name="uq_employee_org_email"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="employees")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    leaves = relationship("EmployeeLeave", back_populates="employee", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="employee", foreign_keys="Assignment.employee_id", cascade="all, delete-orphan")
    mentored_assignments = relationship("Assignment", back_populates="mentor", foreign_keys="Assignment.mentor_id")
    dossier = relationship("EmployeeDossier", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    dossier_documents = relationship("DossierDocument", back_populates="employee", cascade="all, delete-orphan")


class EmployeeLeave(TenantModel):
    __tablename__ = "employee_leaves"

    employee_id = Column(
        String(36),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=True)

    # Relationships
    employee = relationship("Employee", back_populates="leaves")
