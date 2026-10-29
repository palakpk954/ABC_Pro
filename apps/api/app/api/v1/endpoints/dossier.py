from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.dossier import DossierDocument, EmployeeDossier
from app.models.employee import Employee
from app.models.skill import EmployeeSkill, Skill
from app.models.user import User
from app.schemas.dossier import (
    DossierDocumentResponse,
    EmployeeDossierResponse,
    MultiSourceUploadSummary,
    SkillEvidenceItem,
)
from app.services.document_parser import DocumentParser
from app.services.dossier_extractor import DossierExtractor

router = APIRouter()


@router.post("/upload", response_model=MultiSourceUploadSummary)
async def upload_dossier_documents(
    employee_id: str = Form(...),
    category: Optional[str] = Form("auto"),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload one or multiple documents for an employee (Resume, Performance Review,
    360 Feedback, Activity Log, Availability). Parses content, extracts insights,
    and progressively enriches the Living Talent Dossier.
    """
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.org_id == current_user.org_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found."
        )

    processed_filenames = []
    categories_detected = []
    new_extractions = []

    for file in files:
        content = await file.read()
        extracted_text, detected_type = DocumentParser.parse_file(file.filename, content)

        doc_category = category
        if not doc_category or doc_category == "auto":
            doc_category = DocumentParser.infer_document_category(file.filename, extracted_text)

        categories_detected.append(doc_category)
        processed_filenames.append(file.filename)

        # Run cognitive extraction on document
        extraction = DossierExtractor.extract_from_document(
            text=extracted_text,
            category=doc_category,
            filename=file.filename
        )
        new_extractions.append(extraction)

        # Save document record
        doc_record = DossierDocument(
            org_id=current_user.org_id,
            employee_id=employee.id,
            filename=file.filename,
            file_type=detected_type,
            category=doc_category,
            extracted_text=extracted_text,
            parsed_payload=extraction,
        )
        db.add(doc_record)

    # Fetch or create dossier
    existing_dossier = db.query(EmployeeDossier).filter(
        EmployeeDossier.employee_id == employee.id,
        EmployeeDossier.org_id == current_user.org_id
    ).first()

    existing_data = None
    if existing_dossier:
        existing_data = {
            "archetype": existing_dossier.archetype,
            "burnout_risk_score": existing_dossier.burnout_risk_score,
            "burnout_factors": existing_dossier.burnout_factors or [],
            "career_aspirations": existing_dossier.career_aspirations or [],
            "evidence_citations": existing_dossier.evidence_citations or [],
        }

    # Progressive synthesis
    synthesized = DossierExtractor.synthesize_progressive_dossier(existing_data, new_extractions)

    if existing_dossier:
        existing_dossier.archetype = synthesized["archetype"]
        existing_dossier.archetype_rationale = synthesized["archetype_rationale"]
        existing_dossier.burnout_risk_score = synthesized["burnout_risk_score"]
        existing_dossier.burnout_factors = synthesized["burnout_factors"]
        existing_dossier.coaching_sentiment = synthesized["coaching_sentiment"]
        existing_dossier.client_facing_comfort = synthesized["client_facing_comfort"]
        existing_dossier.preferred_team_size = synthesized["preferred_team_size"]
        existing_dossier.strengths_summary = synthesized["strengths_summary"]
        existing_dossier.growth_areas = synthesized["growth_areas"]
        existing_dossier.career_aspirations = synthesized["career_aspirations"]
        existing_dossier.stretch_readiness_score = synthesized["stretch_readiness_score"]
        existing_dossier.profile_summary = synthesized["profile_summary"]
        existing_dossier.confidence_overall = synthesized["confidence_overall"]
        existing_dossier.enrichment_level = synthesized["enrichment_level"]
        existing_dossier.evidence_citations = synthesized["evidence_citations"]
    else:
        new_dossier = EmployeeDossier(
            org_id=current_user.org_id,
            employee_id=employee.id,
            archetype=synthesized["archetype"],
            archetype_rationale=synthesized["archetype_rationale"],
            burnout_risk_score=synthesized["burnout_risk_score"],
            burnout_factors=synthesized["burnout_factors"],
            coaching_sentiment=synthesized["coaching_sentiment"],
            client_facing_comfort=synthesized["client_facing_comfort"],
            preferred_team_size=synthesized["preferred_team_size"],
            strengths_summary=synthesized["strengths_summary"],
            growth_areas=synthesized["growth_areas"],
            career_aspirations=synthesized["career_aspirations"],
            stretch_readiness_score=synthesized["stretch_readiness_score"],
            profile_summary=synthesized["profile_summary"],
            confidence_overall=synthesized["confidence_overall"],
            enrichment_level=synthesized["enrichment_level"],
            evidence_citations=synthesized["evidence_citations"],
        )
        db.add(new_dossier)

    # Sync high-confidence skills to EmployeeSkill relational table
    for sk in synthesized["evidence_citations"]:
        skill_name = sk["skill"]
        skill_obj = db.query(Skill).filter(
            Skill.name == skill_name,
            Skill.org_id == current_user.org_id
        ).first()

        if not skill_obj:
            skill_obj = Skill(
                org_id=current_user.org_id,
                name=skill_name,
                category="General Engineering"
            )
            db.add(skill_obj)
            db.flush()

        emp_skill = db.query(EmployeeSkill).filter(
            EmployeeSkill.employee_id == employee.id,
            EmployeeSkill.skill_id == skill_obj.id,
            EmployeeSkill.org_id == current_user.org_id
        ).first()

        if emp_skill:
            emp_skill.proficiency = sk["proficiency"]
        else:
            emp_skill = EmployeeSkill(
                org_id=current_user.org_id,
                employee_id=employee.id,
                skill_id=skill_obj.id,
                proficiency=sk["proficiency"],
                growth_target=min(5, sk["proficiency"] + 1),
            )
            db.add(emp_skill)

    db.commit()

    return MultiSourceUploadSummary(
        employee_id=employee.id,
        employee_name=employee.name,
        processed_files=processed_filenames,
        categories_detected=list(set(categories_detected)),
        enrichment_level_reached=synthesized["enrichment_level"],
        confidence_overall=synthesized["confidence_overall"],
        archetype=synthesized["archetype"],
        skills_extracted_count=len(synthesized["evidence_citations"]),
        burnout_risk_score=synthesized["burnout_risk_score"],
        message=f"Successfully enriched {employee.name}'s Living Dossier with {len(processed_filenames)} document(s)."
    )


@router.get("/{employee_id}", response_model=EmployeeDossierResponse)
def get_employee_dossier(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full Living Talent Dossier for an employee."""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.org_id == current_user.org_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found."
        )

    dossier = db.query(EmployeeDossier).filter(
        EmployeeDossier.employee_id == employee.id,
        EmployeeDossier.org_id == current_user.org_id
    ).first()

    # Graceful degradation fallback: If no dossier has been synthesized yet,
    # generate a baseline Level 0 Dossier from employee record
    if not dossier:
        skills = db.query(EmployeeSkill).filter(
            EmployeeSkill.employee_id == employee.id,
            EmployeeSkill.org_id == current_user.org_id
        ).all()
        
        citations = []
        for s in skills:
            citations.append({
                "skill": s.skill.name if s.skill else "General",
                "proficiency": s.proficiency,
                "confidence": 0.65,
                "evidence": f"Baseline system profile for {employee.role}",
                "sources": ["baseline_system"]
            })

        dossier = EmployeeDossier(
            org_id=current_user.org_id,
            employee_id=employee.id,
            archetype="Generalist",
            archetype_rationale="Baseline profile created from active HR directory records.",
            burnout_risk_score=0.15,
            burnout_factors=["Standard baseline workload"],
            coaching_sentiment="Collaborative Contributor",
            client_facing_comfort="Moderate",
            preferred_team_size="3-6 members",
            strengths_summary=[f"Core delivery as {employee.role}"],
            growth_areas=["Multi-source evaluation pending upload"],
            career_aspirations=employee.career_goals or ["Continuous skill growth"],
            stretch_readiness_score=0.70,
            profile_summary=f"Baseline profile for {employee.name} ({employee.role}). Upload resumes or reviews to enrich.",
            confidence_overall=0.65,
            enrichment_level=0,
            evidence_citations=citations,
        )
        db.add(dossier)
        db.commit()
        db.refresh(dossier)

    docs = db.query(DossierDocument).filter(
        DossierDocument.employee_id == employee.id,
        DossierDocument.org_id == current_user.org_id
    ).all()

    citations_items = [
        SkillEvidenceItem(
            skill=c.get("skill", ""),
            proficiency=c.get("proficiency", 3),
            confidence=c.get("confidence", 0.65),
            evidence=c.get("evidence", ""),
            sources=c.get("sources", []),
        )
        for c in (dossier.evidence_citations or [])
    ]

    return EmployeeDossierResponse(
        id=dossier.id,
        employee_id=employee.id,
        employee_name=employee.name,
        employee_role=employee.role,
        employee_email=employee.email,
        archetype=dossier.archetype,
        archetype_rationale=dossier.archetype_rationale,
        burnout_risk_score=dossier.burnout_risk_score,
        burnout_factors=dossier.burnout_factors or [],
        coaching_sentiment=dossier.coaching_sentiment,
        client_facing_comfort=dossier.client_facing_comfort,
        preferred_team_size=dossier.preferred_team_size,
        strengths_summary=dossier.strengths_summary or [],
        growth_areas=dossier.growth_areas or [],
        career_aspirations=dossier.career_aspirations or [],
        stretch_readiness_score=dossier.stretch_readiness_score,
        profile_summary=dossier.profile_summary,
        confidence_overall=dossier.confidence_overall,
        enrichment_level=dossier.enrichment_level,
        evidence_citations=citations_items,
        documents=[
            DossierDocumentResponse(
                id=d.id,
                filename=d.filename,
                file_type=d.file_type,
                category=d.category,
                created_at=d.created_at,
            )
            for d in docs
        ],
        created_at=dossier.created_at,
        updated_at=dossier.updated_at,
    )


@router.get("", response_model=List[EmployeeDossierResponse])
def list_dossiers(
    archetype: Optional[str] = None,
    min_burnout: Optional[float] = None,
    enrichment_level: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all Living Talent Dossiers with optional filters."""
    query = db.query(EmployeeDossier).filter(EmployeeDossier.org_id == current_user.org_id)

    if archetype:
        query = query.filter(EmployeeDossier.archetype == archetype)
    if min_burnout is not None:
        query = query.filter(EmployeeDossier.burnout_risk_score >= min_burnout)
    if enrichment_level is not None:
        query = query.filter(EmployeeDossier.enrichment_level == enrichment_level)

    dossiers = query.all()
    results = []

    for d in dossiers:
        emp = d.employee
        citations_items = [
            SkillEvidenceItem(
                skill=c.get("skill", ""),
                proficiency=c.get("proficiency", 3),
                confidence=c.get("confidence", 0.65),
                evidence=c.get("evidence", ""),
                sources=c.get("sources", []),
            )
            for c in (d.evidence_citations or [])
        ]
        results.append(
            EmployeeDossierResponse(
                id=d.id,
                employee_id=d.employee_id,
                employee_name=emp.name if emp else "Unknown",
                employee_role=emp.role if emp else "",
                employee_email=emp.email if emp else "",
                archetype=d.archetype,
                archetype_rationale=d.archetype_rationale,
                burnout_risk_score=d.burnout_risk_score,
                burnout_factors=d.burnout_factors or [],
                coaching_sentiment=d.coaching_sentiment,
                client_facing_comfort=d.client_facing_comfort,
                preferred_team_size=d.preferred_team_size,
                strengths_summary=d.strengths_summary or [],
                growth_areas=d.growth_areas or [],
                career_aspirations=d.career_aspirations or [],
                stretch_readiness_score=d.stretch_readiness_score,
                profile_summary=d.profile_summary,
                confidence_overall=d.confidence_overall,
                enrichment_level=d.enrichment_level,
                evidence_citations=citations_items,
                documents=[],
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
        )

    return results
