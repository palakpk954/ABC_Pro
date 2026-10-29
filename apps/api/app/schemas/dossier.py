from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SkillEvidenceItem(BaseModel):
    skill: str
    proficiency: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str
    sources: List[str] = Field(default_factory=list)


class DossierDocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeDossierResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    employee_role: Optional[str] = None
    employee_email: Optional[str] = None
    
    # Archetype & Persona
    archetype: str
    archetype_rationale: Optional[str] = None
    
    # Burnout & Stress
    burnout_risk_score: float
    burnout_factors: List[str] = Field(default_factory=list)
    
    # Soft skills & Collaboration
    coaching_sentiment: str
    client_facing_comfort: str
    preferred_team_size: str
    strengths_summary: List[str] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)
    
    # Aspirations & Stretch
    career_aspirations: List[str] = Field(default_factory=list)
    stretch_readiness_score: float
    
    # Summary & Confidence
    profile_summary: str
    confidence_overall: float
    enrichment_level: int
    evidence_citations: List[SkillEvidenceItem] = Field(default_factory=list)
    
    # Ingested documents
    documents: List[DossierDocumentResponse] = Field(default_factory=list)
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MultiSourceUploadSummary(BaseModel):
    employee_id: str
    employee_name: str
    processed_files: List[str]
    categories_detected: List[str]
    enrichment_level_reached: int
    confidence_overall: float
    archetype: str
    skills_extracted_count: int
    burnout_risk_score: float
    message: str
