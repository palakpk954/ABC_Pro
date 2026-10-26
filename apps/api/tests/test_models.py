from datetime import date, timedelta
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
    Plan,
    PlanStatus,
    Assignment,
    Scenario,
    AuditLog,
)
from app.core.security import get_password_hash


def test_organization_and_user_creation(db, test_org):
    user = User(
        org_id=test_org.id,
        email="test.user@example.com",
        full_name="Test Resource Manager",
        role=UserRole.RESOURCE_MANAGER,
        hashed_password=get_password_hash("secretpass"),
    )
    db.add(user)
    db.commit()

    saved_user = db.query(User).filter(User.email == "test.user@example.com").first()
    assert saved_user is not None
    assert saved_user.org_id == test_org.id
    assert saved_user.role == UserRole.RESOURCE_MANAGER
    assert saved_user.is_active is True


def test_multi_tenant_isolation(db):
    org1 = Organization(name="Company A")
    org2 = Organization(name="Company B")
    db.add_all([org1, org2])
    db.commit()

    # Create skills in different orgs with same name
    skill1 = Skill(org_id=org1.id, name="Python", category="Backend")
    skill2 = Skill(org_id=org2.id, name="Python", category="Backend")
    db.add_all([skill1, skill2])
    db.commit()

    # Querying org1 only returns org1's skill
    org1_skills = db.query(Skill).filter(Skill.org_id == org1.id).all()
    org2_skills = db.query(Skill).filter(Skill.org_id == org2.id).all()

    assert len(org1_skills) == 1
    assert org1_skills[0].id == skill1.id
    assert len(org2_skills) == 1
    assert org2_skills[0].id == skill2.id


def test_employee_and_skills_creation(db, test_org):
    skill = Skill(org_id=test_org.id, name="React", category="Frontend")
    db.add(skill)
    db.commit()

    employee = Employee(
        org_id=test_org.id,
        name="Alice Engineer",
        email="alice@example.com",
        role="Frontend Engineer",
        cost_per_hour=85.0,
        weekly_capacity_hours=40,
        max_overtime_hours=10,
        start_date=date(2026, 1, 1),
        career_goals=["Next.js", "System Design"],
    )
    db.add(employee)
    db.commit()

    emp_skill = EmployeeSkill(
        org_id=test_org.id,
        employee_id=employee.id,
        skill_id=skill.id,
        proficiency=4,
        growth_target=5,
    )
    db.add(emp_skill)
    db.commit()

    retrieved = db.query(Employee).filter(Employee.id == employee.id).first()
    assert retrieved is not None
    assert len(retrieved.skills) == 1
    assert retrieved.skills[0].proficiency == 4
    assert retrieved.skills[0].growth_target == 5


def test_project_and_roles_creation(db, test_org):
    project = Project(
        org_id=test_org.id,
        name="Alpha Modernization",
        client="Alpha Corp",
        start_date=date(2026, 11, 2),
        end_date=date(2027, 1, 22),
        revenue=150000.0,
        priority=4,
        mandatory=True,
    )
    db.add(project)
    db.commit()

    role = ProjectRole(
        org_id=test_org.id,
        project_id=project.id,
        role_title="Lead Architect",
        hours_per_week=40,
        start_date=date(2026, 11, 2),
        end_date=date(2027, 1, 22),
        is_stretch_allowed=False,
    )
    db.add(role)
    db.commit()

    assert role.id is not None
    assert len(project.roles) == 1
    assert project.mandatory is True


def test_plan_assignment_and_audit_creation(db, test_org):
    plan = Plan(
        org_id=test_org.id,
        name="Q4 Optimized Plan",
        status=PlanStatus.DRAFT,
        horizon_weeks=12,
        start_date=date(2026, 11, 2),
        profit_weight=0.7,
        growth_weight=0.2,
        balance_weight=0.1,
    )
    db.add(plan)
    db.commit()

    audit = AuditLog(
        org_id=test_org.id,
        action="generate_plan",
        entity_type="plan",
        entity_id=plan.id,
        after_state={"status": "draft", "horizon_weeks": 12},
    )
    db.add(audit)
    db.commit()

    saved_audit = db.query(AuditLog).filter(AuditLog.entity_id == plan.id).first()
    assert saved_audit is not None
    assert saved_audit.action == "generate_plan"
    assert saved_audit.after_state["status"] == "draft"
