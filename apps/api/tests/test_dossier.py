import pytest
from app.services.document_parser import DocumentParser
from app.services.dossier_extractor import DossierExtractor


def test_document_parser_category_inference():
    # Test resume detection
    resume_text = "Experience: Senior Backend Developer. Education: B.S. in Computer Science. Built microservices with Python and FastAPI."
    cat = DocumentParser.infer_document_category("john_doe_resume.pdf", resume_text)
    assert cat == "resume"

    # Test performance review detection
    review_text = "Annual Performance Review Q3: Key accomplishments include scaling the auth service. Strengths: strong technical mentorship."
    cat = DocumentParser.infer_document_category("q3_performance_appraisal.docx", review_text)
    assert cat == "performance_report"

    # Test 360 feedback detection
    feedback_text = "Peer feedback for Alice: She is an exceptional mentor who guided junior developers through tough sprint deadlines."
    cat = DocumentParser.infer_document_category("360_colleague_feedback.txt", feedback_text)
    assert cat == "feedback_360"


def test_dossier_extractor_resume():
    sample_resume = """
    Jane Smith - Senior Cloud Architect
    Experience:
    - Pioneered greenfield event-driven architecture using Python, FastAPI, and PostgreSQL.
    - Designed 0-to-1 distributed microservices handling 50k req/sec.
    - Mentored and coached 3 junior engineers on Docker and Kubernetes orchestration.
    - Career goals: Deepening knowledge in Rust and high-throughput systems.
    """
    
    extraction = DossierExtractor.extract_from_document(
        text=sample_resume,
        category="resume",
        filename="jane_smith_cv.pdf"
    )

    assert extraction["category"] == "resume"
    assert extraction["archetype"] in ["Pathfinder", "Mentor"]
    assert len(extraction["extracted_skills"]) > 0
    
    # Check that skills have confidence and evidence
    skill_names = [s["skill"] for s in extraction["extracted_skills"]]
    assert "Python" in skill_names
    assert "PostgreSQL" in skill_names
    
    python_entry = next(s for s in extraction["extracted_skills"] if s["skill"] == "Python")
    assert python_entry["confidence"] >= 0.65
    assert len(python_entry["evidence"]) > 0


def test_dossier_extractor_burnout_detection():
    exhausted_text = """
    Monthly Activity Summary:
    Faced heavy on-call rotations and consecutive overtime for 4 weeks straight.
    Navigating prolonged crunch sprints to meet tight deadlines under high pressure.
    Expressed fatigue and exhaustion in the latest sprint retrospective.
    """

    extraction = DossierExtractor.extract_from_document(
        text=exhausted_text,
        category="activity_log",
        filename="sprint_october_log.txt"
    )

    assert extraction["burnout_risk_score"] >= 0.50
    assert len(extraction["burnout_factors"]) >= 2


def test_progressive_dossier_synthesis():
    # Step 1: Base resume
    resume_ext = DossierExtractor.extract_from_document(
        text="Skills: Python, Docker, React. Built several frontend dashboards.",
        category="resume",
        filename="alex_resume.pdf"
    )
    
    synth_lvl0 = DossierExtractor.synthesize_progressive_dossier(None, [resume_ext])
    assert synth_lvl0["enrichment_level"] == 0
    initial_conf = synth_lvl0["confidence_overall"]

    # Step 2: Performance report corroborates Python and reveals Mentor archetype
    review_ext = DossierExtractor.extract_from_document(
        text="Q3 Performance Appraisal: Alex demonstrated mastery in Python and PostgreSQL. Mentored 2 interns with great patience.",
        category="performance_report",
        filename="alex_q3_review.docx"
    )

    synth_lvl1 = DossierExtractor.synthesize_progressive_dossier(synth_lvl0, [review_ext])
    assert synth_lvl1["enrichment_level"] == 1
    # Confidence should increase due to multi-source verification!
    assert synth_lvl1["confidence_overall"] >= initial_conf

    # Check that Python has multi-source corroboration
    python_skill = next(s for s in synth_lvl1["evidence_citations"] if s["skill"] == "Python")
    assert "performance_report" in python_skill["sources"]
    assert python_skill["confidence"] >= 0.85
