"""
Cognitive Dossier Extractor & Confidence Calibration Engine.

Extracts structured talent insights from unstructured texts (Resumes, Performance Reviews,
360 Feedback, Activity Logs, and 1-on-1s), with progressive profile enrichment,
evidence quotation, and confidence calibration.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


# Known domain skills & tech keywords for robust extraction
SKILL_DICTIONARY = {
    "Python": ["python", "django", "fastapi", "flask", "sqlalchemy", "celery", "pytest"],
    "TypeScript": ["typescript", "ts", "javascript", "js", "node", "nodejs"],
    "React": ["react", "react.js", "next.js", "nextjs", "redux", "tailwind"],
    "PostgreSQL": ["postgresql", "postgres", "sql", "relational database", "rdbms"],
    "Docker": ["docker", "container", "containerization", "docker-compose"],
    "Kubernetes": ["kubernetes", "k8s", "helm", "eks", "gke", "orchestration"],
    "AWS": ["aws", "amazon web services", "s3", "ec2", "lambda", "rds", "cloudformation"],
    "Distributed Systems": ["distributed systems", "microservices", "kafka", "rabbitmq", "grpc", "event-driven"],
    "Machine Learning": ["machine learning", "ml", "ai", "pytorch", "tensorflow", "scikit-learn", "nlp", "llm"],
    "CI/CD": ["ci/cd", "github actions", "gitlab ci", "jenkins", "pipeline", "continuous integration"],
    "System Architecture": ["system design", "architecture", "high availability", "scalability", "ddd"],
    "Golang": ["golang", "go programming", "goroutines"],
    "Rust": ["rust", "cargo", "rustlang"],
    "GraphQL": ["graphql", "apollo", "schema design"],
    "UI/UX Design": ["ui/ux", "figma", "wireframing", "design system", "accessibility"],
    "Project Management": ["scrum", "agile", "jira", "sprint planning", "stakeholder management"],
}

# Archetype indicator keywords
ARCHETYPE_PATTERNS = {
    "Pathfinder": [
        "greenfield", "0 to 1", "0-to-1", "poc", "prototype", "pioneered", "bootstrapped",
        "architected from scratch", "ambiguity", "exploratory", "mvp", "innovated"
    ],
    "Optimizer": [
        "scaled", "optimized", "latency reduction", "throughput", "refactored", "performance tuning",
        "cost reduction", "hardening", "reliability", "infrastructure scaling", "bottlenecks", "1 to 100"
    ],
    "Firefighter": [
        "incident response", "post-mortem", "on-call", "critical bug", "production triage",
        "troubleshooting", "disaster recovery", "crisis", "firefighting", "root cause analysis"
    ],
    "Mentor": [
        "mentored", "coached", "onboarded", "guided junior", "tech talks", "knowledge sharing",
        "pair programming", "culture champion", "documentation", "symposium"
    ],
}

# Burnout / Fatigue risk keywords
BURNOUT_PATTERNS = [
    ("consecutive overtime", 0.35, "Frequently logging overtime in recent periods"),
    ("weekend work", 0.30, "Working during weekends to meet aggressive deadlines"),
    ("exhaustion", 0.40, "Expressed fatigue or exhaustion in feedback"),
    ("heavy on-call", 0.30, "Bearing high on-call rotation stress"),
    ("crunch", 0.25, "Navigating prolonged crunch sprints"),
    ("tight deadlines", 0.15, "Continuous tight deadlines under high pressure"),
    ("understaffed", 0.20, "Operating in understaffed project conditions"),
]


class DossierExtractor:
    """Cognitive extraction and progressive synthesis engine for Living Talent Dossiers."""

    @classmethod
    def extract_from_document(
        cls,
        text: str,
        category: str,
        filename: str,
    ) -> Dict[str, Any]:
        """
        Extract structured insights from a single document.
        """
        lower_text = text.lower()
        
        extracted_skills = cls._extract_skills(text, lower_text, category, filename)
        archetype, archetype_score, rationale = cls._classify_archetype(lower_text)
        burnout_score, burnout_factors = cls._assess_burnout_risk(lower_text)
        collaboration_info = cls._extract_collaboration_and_soft_skills(text, lower_text, category)
        growth_goals, stretch_score = cls._extract_growth_and_aspirations(text, lower_text)

        summary = cls._generate_summary(
            category=category,
            archetype=archetype,
            skills=extracted_skills,
            growth_goals=growth_goals,
            burnout_score=burnout_score
        )

        return {
            "category": category,
            "filename": filename,
            "extracted_skills": extracted_skills,
            "archetype": archetype,
            "archetype_rationale": rationale,
            "burnout_risk_score": burnout_score,
            "burnout_factors": burnout_factors,
            "coaching_sentiment": collaboration_info["coaching_sentiment"],
            "client_facing_comfort": collaboration_info["client_facing_comfort"],
            "preferred_team_size": collaboration_info["preferred_team_size"],
            "strengths": collaboration_info["strengths"],
            "growth_areas": collaboration_info["growth_areas"],
            "career_aspirations": growth_goals,
            "stretch_readiness_score": stretch_score,
            "summary": summary,
        }

    @classmethod
    def _extract_skills(
        cls,
        raw_text: str,
        lower_text: str,
        category: str,
        filename: str
    ) -> List[Dict[str, Any]]:
        """Identify skills, estimate proficiency and extract real text evidence citations."""
        results = []
        sentences = [s.strip() for s in re.split(r"[.\n;]+", raw_text) if len(s.strip()) > 15]

        # Category base confidence
        base_confidence_map = {
            "resume": 0.65,
            "performance_report": 0.90,
            "feedback_360": 0.85,
            "activity_log": 0.80,
            "availability": 0.50,
        }
        base_confidence = base_confidence_map.get(category, 0.70)

        for canonical_skill, keywords in SKILL_DICTIONARY.items():
            found_count = 0
            matching_sentences = []

            for kw in keywords:
                pattern = r"\b" + re.escape(kw) + r"\b"
                matches = re.findall(pattern, lower_text)
                if matches:
                    found_count += len(matches)
                    for sent in sentences:
                        if re.search(pattern, sent, re.IGNORECASE) and sent not in matching_sentences:
                            matching_sentences.append(sent)

            if found_count > 0:
                # Estimate proficiency (1 - 5) based on depth indicators and frequency
                prof = 3  # default intermediate
                evidence = matching_sentences[0] if matching_sentences else f"Mentioned {found_count} times in {category}"

                evidence_lower = evidence.lower()
                if any(w in evidence_lower for w in ["lead", "architect", "expert", "mastery", "principal", "pioneered", "years of experience"]):
                    prof = 5
                elif any(w in evidence_lower for w in ["senior", "proficient", "advanced", "built", "spearheaded", "designed"]):
                    prof = 4
                elif any(w in evidence_lower for w in ["junior", "beginner", "learning", "exposure", "familiar", "assisted"]):
                    prof = 2

                # If found in performance report with positive adjectives, boost confidence
                conf = min(0.98, base_confidence + (0.05 * min(found_count, 3)))

                results.append({
                    "skill": canonical_skill,
                    "proficiency": prof,
                    "confidence": round(conf, 2),
                    "evidence": evidence[:250],
                    "source_category": category,
                    "source_filename": filename,
                })

        return results

    @classmethod
    def _classify_archetype(cls, lower_text: str) -> Tuple[str, float, str]:
        """Classify employee into working archetype based on behavioral indicators."""
        scores = {}
        for archetype, terms in ARCHETYPE_PATTERNS.items():
            count = sum(len(re.findall(r"\b" + re.escape(t) + r"\b", lower_text)) for t in terms)
            scores[archetype] = count

        top_archetype = max(scores, key=scores.get)
        top_score = scores[top_archetype]

        if top_score == 0:
            return "Generalist", 0.5, "Balanced profile without strong specialized archetype signals."

        rationales = {
            "Pathfinder": "Demonstrates strong initiative in greenfield projects, 0-to-1 prototyping, and driving architecture under ambiguity.",
            "Optimizer": "Excels at large-scale optimization, latency reduction, refactoring, and enterprise-grade hardening.",
            "Firefighter": "Proven track record in high-stakes production incident triage, rapid disaster recovery, and urgent stabilization.",
            "Mentor": "Active knowledge multiplier praised for onboarding, coaching rising engineers, and uplifting team standards.",
        }

        return top_archetype, round(min(1.0, 0.6 + 0.1 * top_score), 2), rationales.get(top_archetype, "")

    @classmethod
    def _assess_burnout_risk(cls, lower_text: str) -> Tuple[float, List[str]]:
        """Calculate burnout risk index and specific contributing factors."""
        risk_score = 0.15  # Baseline normal healthy load
        factors = []

        for term, weight, description in BURNOUT_PATTERNS:
            if term in lower_text:
                risk_score += weight
                factors.append(description)

        risk_score = min(0.95, round(risk_score, 2))
        return risk_score, factors

    @classmethod
    def _extract_collaboration_and_soft_skills(
        cls,
        raw_text: str,
        lower_text: str,
        category: str
    ) -> Dict[str, Any]:
        """Extract team chemistry, coaching sentiment, and communication style."""
        # Coaching sentiment
        if any(w in lower_text for w in ["exceptional mentor", "great coach", "onboarded", "guided teammates"]):
            coaching = "Exemplary Coach & Mentor (High Multiplier)"
        elif any(w in lower_text for w in ["collaborative", "team player", "supportive"]):
            coaching = "Strong Collaborative Team Player"
        elif any(w in lower_text for w in ["independent", "solo", "autonomous contributor"]):
            coaching = "High Autonomy Individual Contributor"
        else:
            coaching = "Collaborative Contributor"

        # Client-facing comfort
        if any(w in lower_text for w in ["client-facing", "presented to stakeholders", "customer demos", "stakeholder management"]):
            client_facing = "High (Confident in front of clients & executives)"
        elif any(w in lower_text for w in ["prefers backend", "internal tools", "avoid direct client"]):
            client_facing = "Low (Thrives in pure internal engineering)"
        else:
            client_facing = "Moderate (Effective with technical client peers)"

        # Preferred team size
        if any(w in lower_text for w in ["large cross-functional", "squad of 10", "enterprise teams"]):
            team_size = "Large cross-functional (6-10 members)"
        elif any(w in lower_text for w in ["small pod", "strike team", "tight-knit"]):
            team_size = "Focused strike team (2-4 members)"
        else:
            team_size = "Standard Agile squad (3-6 members)"

        # Strengths & growth areas
        strengths = []
        if "fastapi" in lower_text or "python" in lower_text:
            strengths.append("High-throughput API development & async design")
        if "architecture" in lower_text or "system design" in lower_text:
            strengths.append("System architecture & decoupled service boundaries")
        if "docker" in lower_text or "kubernetes" in lower_text:
            strengths.append("Containerization & modern cloud infrastructure")
        if not strengths:
            strengths.append("Solid domain delivery and consistent execution")

        growth_areas = []
        if any(w in lower_text for w in ["needs improvement", "growth area", "could develop", "next step"]):
            growth_areas.append("Formalizing technical architecture documentation")
        else:
            growth_areas.append("Deepening expertise in distributed systems & high-availability patterns")

        return {
            "coaching_sentiment": coaching,
            "client_facing_comfort": client_facing,
            "preferred_team_size": team_size,
            "strengths": strengths,
            "growth_areas": growth_areas,
        }

    @classmethod
    def _extract_growth_and_aspirations(
        cls,
        raw_text: str,
        lower_text: str
    ) -> Tuple[List[str], float]:
        """Extract explicit and implicit career goals and stretch readiness."""
        aspirations = []
        for tech in ["Rust", "Kubernetes", "Machine Learning", "System Architecture", "Golang", "Distributed Systems"]:
            if tech.lower() in lower_text and any(w in lower_text for w in ["learn", "aspire", "transition", "goal", "target", "curious about", "stretch"]):
                aspirations.append(f"Transitioning / mastering {tech}")

        if not aspirations:
            aspirations.append("Expanding high-throughput cloud infrastructure and leadership scope")

        # Stretch readiness: high if experienced or praised for fast learning
        stretch_score = 0.80 if any(w in lower_text for w in ["fast learner", "quick study", "adaptable", "stepped up"]) else 0.70
        return aspirations, stretch_score

    @classmethod
    def _generate_summary(
        cls,
        category: str,
        archetype: str,
        skills: List[Dict[str, Any]],
        growth_goals: List[str],
        burnout_score: float
    ) -> str:
        """Create a human-readable synthesis summary."""
        skill_names = [s["skill"] for s in skills[:4]]
        skills_str = ", ".join(skill_names) if skill_names else "Core Engineering Stack"
        
        burnout_desc = "Optimal capacity" if burnout_score < 0.35 else ("Moderate workload stress" if burnout_score < 0.65 else "High fatigue risk")
        
        return (
            f"Evaluated as a '{archetype}' profile grounded in {category} analysis. "
            f"Key competencies include {skills_str}. "
            f"Active career vectors: {'; '.join(growth_goals[:2])}. "
            f"Current workload status: {burnout_desc} (Fatigue Index: {int(burnout_score * 100)}%)."
        )

    @classmethod
    def synthesize_progressive_dossier(
        cls,
        existing_dossier_data: Optional[Dict[str, Any]],
        new_extractions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Progressively enrich an existing dossier with newly parsed documents.
        Corroborates skills across multiple sources, adjusts confidence, and merges insights.
        """
        # Start from base or existing
        skill_map: Dict[str, Dict[str, Any]] = {}
        all_evidence = []
        archetype_votes: Dict[str, int] = {}
        burnout_factors_set = set()
        max_burnout = 0.15
        aspirations_set = set()
        strengths_set = set()
        growth_set = set()
        coaching = "Collaborative Contributor"
        client_comfort = "Moderate"
        team_size = "Standard Agile squad (3-6 members)"
        
        # Populate from existing if present
        if existing_dossier_data:
            for s in existing_dossier_data.get("evidence_citations", []):
                skill_map[s["skill"]] = {
                    "skill": s["skill"],
                    "proficiency": s["proficiency"],
                    "confidence": s["confidence"],
                    "evidence": s.get("evidence", ""),
                    "sources": [s.get("source_category", "prior")]
                }
            max_burnout = existing_dossier_data.get("burnout_risk_score", 0.15)
            for f in existing_dossier_data.get("burnout_factors", []):
                burnout_factors_set.add(f)
            for a in existing_dossier_data.get("career_aspirations", []):
                aspirations_set.add(a)

        # Merge each new extraction
        sources_seen = set()
        for ext in new_extractions:
            cat = ext["category"]
            sources_seen.add(cat)
            
            # Archetype voting
            arch = ext.get("archetype", "Generalist")
            archetype_votes[arch] = archetype_votes.get(arch, 0) + (2 if cat == "performance_report" else 1)

            # Burnout merging
            if ext.get("burnout_risk_score", 0) > max_burnout:
                max_burnout = ext["burnout_risk_score"]
            for f in ext.get("burnout_factors", []):
                burnout_factors_set.add(f)

            # Aspirations
            for a in ext.get("career_aspirations", []):
                aspirations_set.add(a)

            for st in ext.get("strengths", []):
                strengths_set.add(st)
            for gr in ext.get("growth_areas", []):
                growth_set.add(gr)

            if cat == "feedback_360":
                coaching = ext.get("coaching_sentiment", coaching)
                client_comfort = ext.get("client_facing_comfort", client_comfort)

            # Skills corroboration
            for sk in ext.get("extracted_skills", []):
                name = sk["skill"]
                if name in skill_map:
                    # Multi-source corroboration boost!
                    curr = skill_map[name]
                    base_conf = max(curr["confidence"], sk["confidence"])
                    curr["confidence"] = min(0.99, round(base_conf + 0.08, 2))
                    # Take higher proficiency if confirmed by performance report
                    if cat == "performance_report":
                        curr["proficiency"] = sk["proficiency"]
                        curr["evidence"] = f"[Verified by {cat}]: {sk['evidence']}"
                    if cat not in curr["sources"]:
                        curr["sources"].append(cat)
                else:
                    skill_map[name] = {
                        "skill": name,
                        "proficiency": sk["proficiency"],
                        "confidence": sk["confidence"],
                        "evidence": sk["evidence"],
                        "sources": [cat]
                    }

        # Determine winning archetype
        final_archetype = max(archetype_votes, key=archetype_votes.get) if archetype_votes else "Generalist"

        # Determine enrichment level:
        # Level 0: Only resume or availability
        # Level 1: Performance report or activity log
        # Level 2: 360 feedback or 3+ distinct source categories
        num_sources = len(sources_seen)
        if "feedback_360" in sources_seen or num_sources >= 3:
            enrichment_level = 2
        elif "performance_report" in sources_seen or "activity_log" in sources_seen:
            enrichment_level = 1
        else:
            enrichment_level = 0

        # Calibrate overall confidence
        avg_skill_conf = (
            sum(s["confidence"] for s in skill_map.values()) / max(1, len(skill_map))
            if skill_map else 0.65
        )
        overall_confidence = round(min(0.98, avg_skill_conf + (0.05 * enrichment_level)), 2)

        citations_list = list(skill_map.values())

        summary = (
            f"Living Dossier actively synthesized from {num_sources} source categories ({', '.join(sorted(sources_seen))}). "
            f"Classified as '{final_archetype}' with {int(overall_confidence * 100)}% overall calibration confidence. "
            f"Demonstrates verified strengths in {', '.join(list(skill_map.keys())[:4])}."
        )

        return {
            "archetype": final_archetype,
            "archetype_rationale": f"Determined via multi-source synthesis across {num_sources} uploaded documents.",
            "burnout_risk_score": max_burnout,
            "burnout_factors": list(burnout_factors_set),
            "coaching_sentiment": coaching,
            "client_facing_comfort": client_comfort,
            "preferred_team_size": team_size,
            "strengths_summary": list(strengths_set)[:5],
            "growth_areas": list(growth_set)[:3],
            "career_aspirations": list(aspirations_set)[:4],
            "stretch_readiness_score": 0.85 if enrichment_level >= 1 else 0.70,
            "profile_summary": summary,
            "confidence_overall": overall_confidence,
            "enrichment_level": enrichment_level,
            "evidence_citations": citations_list,
        }
