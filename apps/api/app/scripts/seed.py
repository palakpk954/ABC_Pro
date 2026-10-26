"""Database seeding script for Allocate

Usage:
    python -m app.scripts.seed
"""

import sys
import os
from datetime import date, timedelta
from typing import Dict, List

# Ensure apps/api is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models import (
    Organization,
    User,
    UserRole,
    Skill,
    Employee,
    EmployeeSkill,
    EmployeeLeave,
    Project,
    ProjectRole,
    ProjectRoleSkill,
)
from app.db.seed_data import (
    DEFAULT_ORG_NAME,
    DEFAULT_START_DATE,
    USERS_DATA,
    SKILLS_DATA,
    EMPLOYEES_RAW,
    PROJECTS_DATA,
    LEAVES_DATA,
)


def seed_database(db: Session) -> Dict[str, int]:
    print("🌱 Starting Allocate database seeding...")

    # Ensure tables exist (especially helpful in dev / sqlite mode)
    Base.metadata.create_all(bind=engine)

    # 1. Organization
    org = db.query(Organization).filter(Organization.name == DEFAULT_ORG_NAME).first()
    if not org:
        org = Organization(name=DEFAULT_ORG_NAME)
        db.add(org)
        db.flush()
        print(f"Created organization: {org.name} ({org.id})")
    else:
        print(f"Using existing organization: {org.name} ({org.id})")

    org_id = org.id

    # 2. Users
    user_count = 0
    for u in USERS_DATA:
        existing_user = db.query(User).filter(User.email == u["email"]).first()
        if not existing_user:
            new_user = User(
                org_id=org_id,
                email=u["email"],
                full_name=u["full_name"],
                role=UserRole(u["role"]),
                hashed_password=get_password_hash(u["password"]),
            )
            db.add(new_user)
            user_count += 1
    db.flush()
    print(f"Created/verified {len(USERS_DATA)} users")

    # 3. Skills
    skill_map: Dict[str, Skill] = {}
    skill_count = 0
    for s in SKILLS_DATA:
        existing_skill = (
            db.query(Skill)
            .filter(Skill.org_id == org_id, Skill.name == s["name"])
            .first()
        )
        if not existing_skill:
            existing_skill = Skill(
                org_id=org_id,
                name=s["name"],
                category=s["category"],
                description=s["description"],
            )
            db.add(existing_skill)
            skill_count += 1
        skill_map[s["name"]] = existing_skill
    db.flush()
    print(f"Created/verified {len(SKILLS_DATA)} skills")

    # 4. Employees & Skills
    employee_records: List[Employee] = []
    emp_count = 0
    emp_skill_count = 0

    for idx, (emp_name, emp_role, cost, career_goals) in enumerate(EMPLOYEES_RAW):
        email = f"{emp_name.lower().replace(' ', '.').replace('\'', '')}@acmeconsulting.com"
        emp = db.query(Employee).filter(Employee.org_id == org_id, Employee.email == email).first()
        
        if not emp:
            emp = Employee(
                org_id=org_id,
                name=emp_name,
                email=email,
                role=emp_role,
                cost_per_hour=cost,
                weekly_capacity_hours=40,
                max_overtime_hours=10,
                start_date=DEFAULT_START_DATE - timedelta(days=180),  # employed for at least 6 months
                career_goals=career_goals,
                is_active=True,
            )
            db.add(emp)
            db.flush()
            emp_count += 1

            # Assign skill proficiencies based on role
            skills_to_assign = []
            if emp_role == "Tech Lead":
                skills_to_assign = [
                    ("System Design", 5, None),
                    ("AWS Cloud", 4, None),
                    ("Docker & K8s", 4, None),
                    ("Python", 4, None),
                    ("Go", 4, None),
                    ("PostgreSQL", 4, None),
                    ("React", 3, None),
                ]
            elif emp_role == "Senior Backend Engineer":
                skills_to_assign = [
                    ("Python", 4 if idx % 2 == 0 else 5, None),
                    ("Go", 4 if idx % 3 == 0 else 3, None),
                    ("FastAPI", 4, None),
                    ("PostgreSQL", 4, None),
                    ("Docker & K8s", 3 if idx % 2 == 0 else 4, None),
                    ("AWS Cloud", 3, None),
                ]
            elif emp_role == "Senior Frontend Engineer":
                skills_to_assign = [
                    ("React", 5, None),
                    ("TypeScript", 4 if idx % 2 == 0 else 5, None),
                    ("Next.js", 4, None),
                    ("React Native", 3 if idx % 2 == 0 else 4, None),
                    ("FastAPI", 2, None),
                ]
            elif emp_role == "Fullstack Engineer":
                skills_to_assign = [
                    ("React", 3 if idx % 2 == 0 else 4, None),
                    ("TypeScript", 3, None),
                    ("FastAPI", 3, None),
                    ("Python", 3, None),
                    ("PostgreSQL", 3, None),
                    ("Docker & K8s", 2, None),
                ]
            else:  # Associate Engineer
                skills_to_assign = [
                    ("React", 2, 4 if "React" in career_goals else None),
                    ("Python", 2 if idx % 2 == 0 else 3, 4 if "Python" in career_goals else None),
                    ("TypeScript", 2, 4 if "TypeScript" in career_goals else None),
                    ("PostgreSQL", 2, 3),
                    ("FastAPI", 2, 4 if "FastAPI" in career_goals else None),
                ]

            # Also set growth targets for explicit career_goals
            for goal_skill in career_goals:
                if goal_skill in skill_map:
                    # Check if already in skills_to_assign
                    found = False
                    for i, (s_name, prof, target) in enumerate(skills_to_assign):
                        if s_name == goal_skill:
                            skills_to_assign[i] = (s_name, prof, max(prof + 1, 4))
                            found = True
                            break
                    if not found:
                        skills_to_assign.append((goal_skill, 2, 4))

            for s_name, prof, target in skills_to_assign:
                if s_name in skill_map:
                    emp_skill = EmployeeSkill(
                        org_id=org_id,
                        employee_id=emp.id,
                        skill_id=skill_map[s_name].id,
                        proficiency=prof,
                        growth_target=target,
                    )
                    db.add(emp_skill)
                    emp_skill_count += 1
        
        employee_records.append(emp)
    db.flush()
    print(f"Created/verified {len(employee_records)} employees and {emp_skill_count} employee skill proficiencies")

    # 5. Leaves
    leave_count = 0
    for emp_idx, start_wk, num_wks, reason in LEAVES_DATA:
        if emp_idx < len(employee_records):
            emp = employee_records[emp_idx]
            leave_start = DEFAULT_START_DATE + timedelta(weeks=start_wk - 1)
            leave_end = leave_start + timedelta(weeks=num_wks) - timedelta(days=1)
            
            existing_leave = db.query(EmployeeLeave).filter(
                EmployeeLeave.org_id == org_id,
                EmployeeLeave.employee_id == emp.id,
                EmployeeLeave.start_date == leave_start,
            ).first()

            if not existing_leave:
                new_leave = EmployeeLeave(
                    org_id=org_id,
                    employee_id=emp.id,
                    start_date=leave_start,
                    end_date=leave_end,
                    reason=reason,
                )
                db.add(new_leave)
                leave_count += 1
    db.flush()
    print(f"Created/verified {leave_count} employee leave periods")

    # 6. Projects & Roles
    project_count = 0
    role_count = 0
    req_count = 0

    for p in PROJECTS_DATA:
        p_start = DEFAULT_START_DATE + timedelta(weeks=p["start_week"] - 1)
        p_end = DEFAULT_START_DATE + timedelta(weeks=p["end_week"]) - timedelta(days=1)
        
        existing_proj = db.query(Project).filter(
            Project.org_id == org_id,
            Project.name == p["name"],
        ).first()

        if not existing_proj:
            proj = Project(
                org_id=org_id,
                name=p["name"],
                client=p["client"],
                start_date=p_start,
                end_date=p_end,
                revenue=p["revenue"],
                priority=p["priority"],
                mandatory=p["mandatory"],
                status=p["status"],
            )
            db.add(proj)
            db.flush()
            project_count += 1

            for r in p["roles"]:
                role = ProjectRole(
                    org_id=org_id,
                    project_id=proj.id,
                    role_title=r["title"],
                    hours_per_week=r["hours"],
                    start_date=p_start,
                    end_date=p_end,
                    is_stretch_allowed=r["stretch"],
                )
                db.add(role)
                db.flush()
                role_count += 1

                for skill_name, min_prof in r["skills"]:
                    if skill_name in skill_map:
                        req = ProjectRoleSkill(
                            org_id=org_id,
                            project_role_id=role.id,
                            skill_id=skill_map[skill_name].id,
                            min_proficiency=min_prof,
                        )
                        db.add(req)
                        req_count += 1
    
    db.commit()
    print(f"Created/verified {project_count} projects, {role_count} roles, and {req_count} skill requirements")
    print("Seeding complete successfully!")

    return {
        "organizations": 1,
        "users": len(USERS_DATA),
        "skills": len(SKILLS_DATA),
        "employees": len(employee_records),
        "projects": len(PROJECTS_DATA),
        "roles": role_count,
        "leaves": leave_count,
    }


def main():
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}", file=sys.stderr)
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    main()
