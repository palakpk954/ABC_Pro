from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Organization(BaseModel):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False, unique=True, index=True)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="organization", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")
