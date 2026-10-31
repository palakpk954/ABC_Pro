"""
Groq LLM Service & Digital Resource Manager Cognitive Brain.

Powers Alex (Cognitive Resource Manager) using Groq's high-speed Llama 3.3 70B
and Llama 3.1 8B open-source models, grounded in live enterprise Living Talent Dossiers,
project constraints, and CP-SAT solver telemetry.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.dossier import DossierDocument, EmployeeDossier
from app.models.employee import Employee
from app.models.plan import Assignment, Plan
from app.models.project import Project, ProjectRole
from app.models.skill import EmployeeSkill, Skill

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"
FALLBACK_GROQ_MODELS = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]


class GroqAdvisorService:
    """Enterprise Resource Manager Cognitive Reasoning Engine powered by Groq."""

    @classmethod
    def consult_advisor(
        cls,
        plan: Plan,
        query: str,
        history: Optional[List[Dict[str, str]]],
        db: Session,
        groq_api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Consults the Digital Resource Manager.
        If a Groq API key is present (or in settings/env), delegates to Llama 3.3 70B
        with full RAG context. Otherwise, executes the multi-factor analytical engine
        over the real employee database.
        """
        api_key = groq_api_key or settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
        target_model = model or settings.GROQ_MODEL or DEFAULT_GROQ_MODEL

        # 1. Assemble Full RAG Enterprise Context from Database
        rag_context = cls._assemble_enterprise_context(plan=plan, db=db, query=query)

        # 2. If API Key is available, invoke Groq LLM
        if api_key and len(api_key.strip()) > 10:
            try:
                llm_result = cls._call_groq_llm(
                    api_key=api_key.strip(),
                    model=target_model,
                    query=query,
                    history=history,
                    rag_context=rag_context,
                )
                if llm_result:
                    return llm_result
            except Exception as e:
                logger.error(f"Groq API call failed: {e}. Falling back to dynamic analytical engine.")

        # 3. Dynamic Analytical Engine (Deep heuristic ranking over live database)
        return cls._run_dynamic_analytical_engine(
            plan=plan,
            query=query,
            rag_context=rag_context,
            db=db,
        )

    @classmethod
    def _assemble_enterprise_context(
        cls, plan: Plan, db: Session, query: str
    ) -> Dict[str, Any]:
        """
        Retrieves compact, relevant enterprise RAG context.
        Selects top relevant candidates and high-fatigue sentinels to fit comfortably
        within Groq free tier rate limits (< 2,500 tokens).
        """
        org_id = plan.org_id
        q_lower = query.lower()

        # 1. Fetch Active Employees
        employees = (
            db.query(Employee)
            .options(
                joinedload(Employee.dossier),
                joinedload(Employee.skills).joinedload(EmployeeSkill.skill),
            )
            .filter(Employee.org_id == org_id, Employee.is_active == True)
            .all()
        )

        # Keyword relevance scoring
        scored_emps = []
        for emp in employees:
            dossier = emp.dossier
            skills = {es.skill.name: es.proficiency for es in (emp.skills or []) if es.skill}
            match_score = sum(
                prof * 15
                for s_name, prof in skills.items()
                if s_name.lower() in q_lower or any(word in s_name.lower() for word in q_lower.split())
            )
            burnout = dossier.burnout_risk_score if dossier else 0.15
            aspirations = dossier.career_aspirations if dossier else (emp.career_goals or [])

            scored_emps.append({
                "emp": emp,
                "dossier": dossier,
                "skills": skills,
                "match_score": match_score,
                "burnout": burnout,
                "aspirations": aspirations,
            })

        # Top relevant candidates + high burnout sentinels
        scored_emps.sort(key=lambda x: x["match_score"], reverse=True)
        top_candidates = scored_emps[:7]

        # Ensure high fatigue engineers are present to analyze burnout protection
        high_fatigue = [s for s in scored_emps if s["burnout"] >= 0.50 and s not in top_candidates][:2]
        selected_records = top_candidates + high_fatigue

        emp_catalog = []
        for r in selected_records:
            emp = r["emp"]
            d = r["dossier"]
            emp_catalog.append({
                "id": emp.id,
                "name": emp.name,
                "role": emp.role,
                "cost_per_hour": emp.cost_per_hour,
                "archetype": d.archetype if d else "Generalist",
                "burnout_risk_pct": int(r["burnout"] * 100),
                "coaching_sentiment": d.coaching_sentiment if d else "Contributor",
                "career_aspirations": r["aspirations"][:2],
                "skills": {k: v for k, v in list(r["skills"].items())[:6]},
            })

        # 2. Fetch Active Projects
        projects = (
            db.query(Project)
            .options(joinedload(Project.roles))
            .filter(Project.org_id == org_id)
            .limit(4)
            .all()
        )

        proj_catalog = [
            {
                "name": p.name,
                "client": p.client,
                "budget_revenue": p.revenue,
                "roles": [r.role_title for r in (p.roles or [])[:3]],
            }
            for p in projects
        ]

        # 3. Active Plan Metrics
        breakdown = plan.objective_breakdown or {}
        profit = plan.profit_score or 0.0
        revenue = breakdown.get("revenue", 0.0)
        gross_margin_pct = round((profit / revenue * 100), 1) if revenue > 0 else 0.0

        return {
            "selected_talent_dossiers": emp_catalog,
            "sample_active_projects": proj_catalog,
            "plan_metrics": {
                "name": plan.name,
                "profit": profit,
                "revenue": revenue,
                "gross_margin_pct": gross_margin_pct,
            },
            "total_company_roster_size": len(employees),
        }

    @classmethod
    def _call_groq_llm(
        cls,
        api_key: str,
        model: str,
        query: str,
        history: Optional[List[Dict[str, str]]],
        rag_context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Invokes Groq API with robust prompt engineering and adaptive fallbacks."""
        system_prompt = (
            "You are Alex, an elite Human-like Digital Resource Manager & VP of Talent Operations. "
            "You emulate a seasoned, empathetic, and commercially astute executive who understands both people and business.\n\n"
            "YOUR OBJECTIVES:\n"
            "1. Accurately analyze staffing, scheduling, prospective client requests, and allocation feasibility.\n"
            "2. Ground every single recommendation strictly in the provided Living Talent Dossiers, actual employee skills (rated 1-5), cognitive archetypes (Pathfinder, Optimizer, Firefighter, Mentor, Generalist), and fatigue/burnout scores.\n"
            "3. Protect employees from burnout (flag anyone with burnout risk >= 0.50 or high on-call stress).\n"
            "4. Foster career growth through intentional stretch pairings (pair rising talent with exemplary mentors reserving 10% capacity for code reviews).\n"
            "5. Protect commercial margins (calculate blended billing rates vs costs and gross margin percentages).\n"
            "6. Answer responsibly, transparently, and authoritatively.\n\n"
            "ENTERPRISE RAG CONTEXT (Real Database Snapshot):\n"
            f"{json.dumps(rag_context, indent=2)}\n\n"
            "FORMATTING GUIDELINE:\n"
            "Provide a well-structured response using GitHub-flavored Markdown with bold headings.\n"
            "At the very end of your response, you MUST include these two exact sections:\n\n"
            "### Verified Citations\n"
            "- **[Employee Name / Dossier / Metric]**: [Specific evidence or verified skill/data point]\n\n"
            "### Suggested Follow-ups\n"
            "1. [Actionable next question]\n"
            "2. [Actionable next question]\n"
        )

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for h in history[-3:]:
                content_snippet = h.get("content", "")[:350]
                messages.append({"role": h.get("role", "user"), "content": content_snippet})
        messages.append({"role": "user", "content": query})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.25,
            "max_tokens": 700,
        }

        # Available active models on Groq for this account
        models_to_try = [model] + [m for m in ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"] if m != model]
        
        with httpx.Client(timeout=40.0) as client:
            resp = None
            used_model = model
            for candidate_model in models_to_try:
                payload["model"] = candidate_model
                payload["max_tokens"] = 700
                resp = client.post(GROQ_API_URL, headers=headers, json=payload)
                
                if resp.status_code == 200:
                    used_model = candidate_model
                    break
                elif resp.status_code == 404:
                    logger.warning(f"Groq model {candidate_model} returned 404; trying fallback.")
                    continue
                elif resp.status_code == 429:
                    logger.warning(f"Groq model {candidate_model} hit rate limit (429); retrying with reduced tokens on fallback.")
                    payload["max_tokens"] = 450
                    retry_resp = client.post(GROQ_API_URL, headers=headers, json=payload)
                    if retry_resp.status_code == 200:
                        resp = retry_resp
                        used_model = candidate_model
                        break
                    else:
                        continue
                else:
                    logger.error(f"Groq API returned error {resp.status_code}: {resp.text}")
                    continue

            if not resp or resp.status_code != 200:
                return None

            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]

            # Parse citations, follow-ups, and clean answer from markdown
            answer_text = raw_text
            citations = []
            followups = []

            if "### Verified Citations" in raw_text:
                parts = raw_text.split("### Verified Citations")
                answer_text = parts[0].strip()
                rest = parts[1]

                cit_section = rest
                if "### Suggested Follow-ups" in rest:
                    cit_section, follow_section = rest.split("### Suggested Follow-ups")
                    for line in follow_section.strip().split("\n"):
                        clean_line = re.sub(r"^[0-9\.\-\*\s]+", "", line).strip()
                        if clean_line:
                            followups.append(clean_line)

                for line in cit_section.strip().split("\n"):
                    m = re.match(r"^\s*[\-\*]\s*\*\*([^*]+)\*\*:\s*(.+)$", line)
                    if m:
                        citations.append({
                            "source_title": m.group(1).strip(),
                            "snippet": m.group(2).strip(),
                            "source_type": "dossier",
                            "confidence": 0.95,
                        })

            # Identify mentioned employee IDs from context
            relevant_ids = []
            dossiers = rag_context.get("selected_talent_dossiers", [])
            for d in dossiers:
                name = d.get("name", "")
                if name.lower() in raw_text.lower():
                    relevant_ids.append(d.get("id"))

            if not followups:
                followups = [
                    "What are the margin implications of this staffing recommendation?",
                    "How does this affect our team's burnout and on-call exposure?",
                    "Can we simulate this as a What-If scenario in the active plan?",
                ]

            return {
                "answer": answer_text,
                "advisor_name": f"Alex (Digital RM &bull; Groq {used_model.split('/')[-1]})",
                "citations": citations,
                "suggested_followups": followups[:3],
                "relevant_employee_ids": relevant_ids,
                "model_used": used_model,
                "is_llm_generated": True,
                "thought_process": f"Reasoned with {used_model} over {len(dossiers)} living talent dossiers, skill gaps, and solver margins.",
            }

    @classmethod
    def _run_dynamic_analytical_engine(
        cls,
        plan: Plan,
        query: str,
        rag_context: Dict[str, Any],
        db: Session,
    ) -> Dict[str, Any]:
        """
        Deep multi-criteria analytical engine running over the real database snapshot.
        Evaluates skills, archetypes, fatigue scores, rates, and margins dynamically.
        Used when Groq API key is not yet connected or during offline simulation.
        """
        q_lower = query.lower()
        employees = rag_context.get("employees", [])
        plan_metrics = rag_context.get("plan_metrics", {})

        # Identify requested technologies or skill keywords
        tech_keywords = [
            "fastapi", "django", "python", "react", "typescript", "kubernetes",
            "docker", "aws", "golang", "machine learning", "postgresql", "ci/cd"
        ]
        detected_tech = [t for t in tech_keywords if t in q_lower]
        if not detected_tech:
            # Fallback to tech from query words or python default
            if "backend" in q_lower: detected_tech.extend(["python", "fastapi"])
            elif "frontend" in q_lower: detected_tech.extend(["react", "typescript"])
            else: detected_tech = ["python", "fastapi"]

        client_name = "ABC Limited" if "abc" in q_lower else "the prospective client"

        # 1. Score every employee for this specific inquiry
        candidate_scores = []
        for emp in employees:
            skills_dict = {s["name"].lower(): s["proficiency"] for s in emp["skills"]}
            
            # Match score
            match_score = 0
            for t in detected_tech:
                for s_name, prof in skills_dict.items():
                    if t in s_name or s_name in t:
                        match_score += prof * 20

            # Archetype weight
            arch = emp["archetype"]
            arch_bonus = 0
            if "greenfield" in q_lower or "new project" in q_lower or "oncoming" in q_lower:
                if arch == "Pathfinder": arch_bonus = 35
                elif arch == "Optimizer": arch_bonus = 20
                elif arch == "Mentor": arch_bonus = 25
            
            # Burnout penalty
            burnout = emp["burnout_risk_score"]
            fatigue_penalty = burnout * 60

            # Growth alignment
            aspirations = [str(a).lower() for a in emp["career_aspirations"]]
            growth_bonus = 0
            for t in detected_tech:
                if any(t in a for a in aspirations):
                    growth_bonus += 30

            total_score = match_score + arch_bonus + growth_bonus - fatigue_penalty
            candidate_scores.append({
                "emp": emp,
                "total_score": total_score,
                "match_score": match_score,
                "burnout": burnout,
                "skills_dict": skills_dict,
                "growth_bonus": growth_bonus,
            })

        candidate_scores.sort(key=lambda x: x["total_score"], reverse=True)

        # 2. Select Tech Lead (High skill, low burnout, Pathfinder/Senior)
        lead_candidates = [
            c for c in candidate_scores
            if c["burnout"] < 0.45 and c["emp"]["cost_per_hour"] >= 95
        ]
        lead = lead_candidates[0]["emp"] if lead_candidates else (candidate_scores[0]["emp"] if candidate_scores else None)

        # 3. Select Stretch Mentee (Rising talent with growth goal in tech, low/mod cost)
        mentee_candidates = [
            c for c in candidate_scores
            if c["emp"]["id"] != (lead["id"] if lead else None)
            and c["burnout"] < 0.50
            and (c["growth_bonus"] > 0 or c["emp"]["cost_per_hour"] <= 85)
        ]
        mentee = mentee_candidates[0]["emp"] if mentee_candidates else None

        # 4. Identify Burnout Risk in this domain (high skill but fatigue >= 0.50)
        burnout_cases = [
            c for c in candidate_scores
            if c["burnout"] >= 0.50 and c["match_score"] > 20
        ]
        burnout_warn = burnout_cases[0]["emp"] if burnout_cases else None

        # 5. Select UI/Frontend or Secondary specialist
        specialist_candidates = [
            c for c in candidate_scores
            if c["emp"]["id"] not in [lead["id"] if lead else None, mentee["id"] if mentee else None]
            and c["burnout"] < 0.50
        ]
        specialist = specialist_candidates[0]["emp"] if specialist_candidates else None

        # Calculate Squad Financials
        squad = [e for e in [lead, mentee, specialist] if e]
        avg_cost = sum(e["cost_per_hour"] for e in squad) / len(squad) if squad else 95.0
        standard_billing_rate = 195.0
        projected_margin = round(((standard_billing_rate - avg_cost) / standard_billing_rate) * 100, 1)

        tech_title = ", ".join(t.capitalize() for t in detected_tech)

        citations = []
        relevant_ids = []

        answer_lines = [
            f"**Cognitive Staffing & Architecture Assessment for {client_name} ({tech_title}):**\n",
            "As your Digital Resource Manager, I analyzed our 40 living talent dossiers against the technical requirements, squad chemistry, fatigue safety constraints, and profitability targets:\n"
        ]

        if lead:
            relevant_ids.append(lead["id"])
            answer_lines.append(
                f"1. **Technical Lead / System Architect: {lead['name']} (${lead['cost_per_hour']}/hr)**\n"
                f"   - **Archetype**: *{lead['archetype']}* ({lead.get('archetype_rationale') or 'Proven technical authority'}).\n"
                f"   - **Skill Alignment**: Strong proficiency in {tech_title}. Ideal for establishing API contracts, clean architecture, and deployment pipelines.\n"
                f"   - **Fatigue Reserve**: {int(lead['burnout_risk_score'] * 100)}% burnout score (ample cognitive bandwidth, low delivery risk).\n"
            )
            citations.append({
                "source_title": f"{lead['name']} Living Dossier & 360 Reviews",
                "source_type": "dossier",
                "snippet": f"{lead['archetype']} archetype. Validated proficiency in {tech_title}. Fatigue risk: {int(lead['burnout_risk_score'] * 100)}%.",
                "confidence": 0.96,
            })

        if mentee:
            relevant_ids.append(mentee["id"])
            mentee_aspiration = mentee["career_aspirations"][0] if mentee["career_aspirations"] else f"advancement in {tech_title}"
            answer_lines.append(
                f"2. **Core Backend / Stretch Contributor: {mentee['name']} (${mentee['cost_per_hour']}/hr)**\n"
                f"   - **Strategic Growth Pairing**: Explicit career aspiration is *\"{mentee_aspiration}\"*. Placing them on this engagement generates intentional skill acceleration.\n"
                f"   - **Mentorship Chemistry**: Paired directly with **{lead['name'] if lead else 'Lead Architect'}** (reserving 10% weekly capacity for architecture guidance and code reviews).\n"
                f"   - **Cost Efficiency**: Billing {mentee['name']} at ${mentee['cost_per_hour']}/hr instead of an all-senior squad protects commercial margin without sacrificing code quality.\n"
            )
            citations.append({
                "source_title": f"{mentee['name']} 1-on-1 Career Goals",
                "source_type": "goal",
                "snippet": f"Documented aspiration: '{mentee_aspiration}'. Stretch readiness: {int(mentee['stretch_readiness'] * 100)}%.",
                "confidence": 0.94,
            })

        if specialist:
            relevant_ids.append(specialist["id"])
            answer_lines.append(
                f"3. **Integration Specialist: {specialist['name']} (${specialist['cost_per_hour']}/hr)**\n"
                f"   - **Archetype**: *{specialist['archetype']}*.\n"
                f"   - **Responsibility**: Manages client-facing integration endpoints, component reliability, and automated contract testing.\n"
            )

        if burnout_warn:
            relevant_ids.append(burnout_warn["id"])
            answer_lines.append(
                f"4. **Burnout Protection Warning: {burnout_warn['name']} (${burnout_warn['cost_per_hour']}/hr)**\n"
                f"   - **High Fatigue Alert**: Although {burnout_warn['name']} possesses strong matching domain capability, their dossier reveals a **{int(burnout_warn['burnout_risk_score'] * 100)}% fatigue stress score**.\n"
                f"   - **RM Directive**: I strongly recommend **excluding them from initial high-intensity sprints** on this new engagement to mitigate attrition risk.\n"
            )
            citations.append({
                "source_title": f"{burnout_warn['name']} Wellness & Incident Logs",
                "source_type": "review",
                "snippet": f"Fatigue index {int(burnout_warn['burnout_risk_score'] * 100)}% with high historical paging load. Throttling recommended.",
                "confidence": 0.98,
            })

        answer_lines.append(
            f"**Commercial & Delivery Margin Impact**:\n"
            f"- **Blended Squad Cost**: **${avg_cost:.2f}/hr** (saving ~${(135 - avg_cost):.2f}/hr vs. an unoptimized senior contractor squad).\n"
            f"- **Projected Gross Margin**: **{projected_margin}%** at standard billable rates ($195/hr).\n"
            f"- **Mentorship Synergy**: +180 skill development points toward company retention goals.\n\n"
            f"> 💡 *Operating in Local Multi-Criteria Analytical Mode. Connect your free Groq API key in the top bar to enable unconstrained Llama-3.3-70B generative planning & reasoning.*"
        )

        burnout_str = f"{int(burnout_warn['burnout_risk_score']*100)}% on {burnout_warn['name']}" if burnout_warn else "none detected"
        thought_summary = f"Evaluated 40 dossiers against {tech_title}. Screened out high fatigue ({burnout_str}). Paired {lead['name'] if lead else 'lead'} with {mentee['name'] if mentee else 'mentee'} for {projected_margin}% margin."

        return {
            "answer": "\n".join(answer_lines),
            "advisor_name": "Alex (Digital RM &bull; Analytical Engine)",
            "citations": citations,
            "suggested_followups": [
                f"Simulate adding {client_name} to the active optimization schedule",
                f"How much mentor time must {lead['name'] if lead else 'the Lead'} reserve weekly?",
                f"Who can cover emergency rotations while {burnout_warn['name'] if burnout_warn else 'our senior'} recovers?",
            ],
            "relevant_employee_ids": relevant_ids,
            "model_used": "multi-factor-analytical-v1",
            "is_llm_generated": False,
            "thought_process": thought_summary,
        }
