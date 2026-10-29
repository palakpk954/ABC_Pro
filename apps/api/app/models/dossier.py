from sqlalchemy import (
    JSON,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models.base import TenantModel


class DossierDocument(TenantModel):
    """Stores uploaded raw documents associated with an employee or organization."""
    __tablename__ = "dossier_documents"

    employee_id = Column(
        String(36),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, json, csv, text
    category = Column(String(50), nullable=False)   # resume, performance_report, feedback_360, activity_log, availability
    extracted_text = Column(Text, nullable=False)
    parsed_payload = Column(JSON, nullable=False, default=dict)

    # Relationships
    employee = relationship("Employee", back_populates="dossier_documents")


class EmployeeDossier(TenantModel):
    """
    Living Talent Dossier: Synthesizes multi-source qualitative and quantitative
    signals into a holistic employee persona.
    """
    __tablename__ = "employee_dossiers"

    employee_id = Column(
        String(36),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    
    # Cognitive Archetype & Working Style
    archetype = Column(String(100), nullable=False, default="Generalist")  # Pathfinder, Optimizer, Firefighter, Mentor, Generalist
    archetype_rationale = Column(Text, nullable=True)

    # Burnout & Fatigue Risk
    burnout_risk_score = Column(Float, nullable=False, default=0.15)  # 0.0 - 1.0
    burnout_factors = Column(JSON, nullable=False, default=list)

    # Collaboration & Soft Skills
    coaching_sentiment = Column(String(255), nullable=False, default="Collaborative Contributor")
    client_facing_comfort = Column(String(50), nullable=False, default="Moderate")  # High, Moderate, Low
    preferred_team_size = Column(String(50), nullable=False, default="3-6 members")
    strengths_summary = Column(JSON, nullable=False, default=list)
    growth_areas = Column(JSON, nullable=False, default=list)

    # Career Aspirations & Learning Vectors
    career_aspirations = Column(JSON, nullable=False, default=list)
    stretch_readiness_score = Column(Float, nullable=False, default=0.75)

    # Overall Metrics & Confidence
    profile_summary = Column(Text, nullable=False, default="")
    confidence_overall = Column(Float, nullable=False, default=0.70)
    enrichment_level = Column(Integer, nullable=False, default=0)  # 0: Basic/Resume, 1: Performance/Activity, 2: 360/Full
    evidence_citations = Column(JSON, nullable=False, default=list)

    # Relationships
    employee = relationship("Employee", back_populates="dossier")
