import enum
from sqlalchemy import Column, String, Integer, Float, Date, Boolean, JSON, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app.models.base import TenantModel


class PlanStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class Plan(TenantModel):
    __tablename__ = "plans"

    name = Column(String(255), nullable=False, default="Staffing Plan")
    status = Column(Enum(PlanStatus), default=PlanStatus.DRAFT, nullable=False, index=True)
    horizon_weeks = Column(Integer, nullable=False, default=12)
    start_date = Column(Date, nullable=False)
    
    # Objective weights (0.0 to 1.0)
    profit_weight = Column(Float, nullable=False, default=0.6)
    growth_weight = Column(Float, nullable=False, default=0.3)
    balance_weight = Column(Float, nullable=False, default=0.1)

    # Optimization score breakdown
    total_score = Column(Float, nullable=True)
    profit_score = Column(Float, nullable=True)
    growth_score = Column(Float, nullable=True)
    balance_penalty = Column(Float, nullable=True)

    # Solver metrics
    solver_status = Column(String(50), nullable=True)  # OPTIMAL, FEASIBLE, INFEASIBLE, etc.
    solver_gap = Column(Float, nullable=True)
    solver_wall_time_ms = Column(Float, nullable=True)
    inputs_hash = Column(String(64), nullable=True)

    # Detailed solver outputs
    objective_breakdown = Column(JSON, nullable=True)
    dropped_project_reasons = Column(JSON, nullable=True)

    # Governance
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="plans")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    assignments = relationship("Assignment", back_populates="plan", cascade="all, delete-orphan")
    scenarios_as_base = relationship("Scenario", foreign_keys="Scenario.base_plan_id", back_populates="base_plan", cascade="all, delete-orphan")
    scenarios_as_modified = relationship("Scenario", foreign_keys="Scenario.modified_plan_id", back_populates="modified_plan")


class Assignment(TenantModel):
    __tablename__ = "assignments"

    plan_id = Column(
        String(36),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    employee_id = Column(
        String(36),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_role_id = Column(
        String(36),
        ForeignKey("project_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week_number = Column(Integer, nullable=False)  # 1 to horizon_weeks
    hours = Column(Integer, nullable=False)
    is_stretch = Column(Boolean, nullable=False, default=False)
    mentor_id = Column(
        String(36),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_locked = Column(Boolean, nullable=False, default=False)
    reasons = Column(JSON, nullable=True)  # Structured explanation

    # Relationships
    plan = relationship("Plan", back_populates="assignments")
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="assignments")
    mentor = relationship("Employee", foreign_keys=[mentor_id], back_populates="mentored_assignments")
    project_role = relationship("ProjectRole", back_populates="assignments")


class Scenario(TenantModel):
    __tablename__ = "scenarios"

    base_plan_id = Column(
        String(36),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    modified_plan_id = Column(
        String(36),
        ForeignKey("plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    modifications = Column(JSON, nullable=False, default=dict)  # modified parameters
    diff_summary = Column(JSON, nullable=True)  # profit delta, growth delta, assignments changed
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    base_plan = relationship("Plan", foreign_keys=[base_plan_id], back_populates="scenarios_as_base")
    modified_plan = relationship("Plan", foreign_keys=[modified_plan_id], back_populates="scenarios_as_modified")
    creator = relationship("User", foreign_keys=[created_by])
