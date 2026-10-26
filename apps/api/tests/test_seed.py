from app.scripts.seed import seed_database
from app.models import Organization, User, Skill, Employee, Project, EmployeeLeave, ProjectRole


def test_seed_database_executes_and_populates_data(db):
    results = seed_database(db)

    # 1. Organization
    org = db.query(Organization).first()
    assert org is not None
    assert org.name == "Acme Consulting Services"

    # 2. Users
    users = db.query(User).filter(User.org_id == org.id).all()
    assert len(users) >= 4
    roles = {u.role.value for u in users}
    assert "resource_manager" in roles
    assert "delivery_head" in roles

    # 3. Skills
    skills = db.query(Skill).filter(Skill.org_id == org.id).all()
    assert len(skills) >= 12

    # 4. Employees: exactly 40 employees across 5 roles
    employees = db.query(Employee).filter(Employee.org_id == org.id).all()
    assert len(employees) == 40
    emp_roles = {e.role for e in employees}
    assert len(emp_roles) == 5
    assert "Tech Lead" in emp_roles
    assert "Senior Backend Engineer" in emp_roles
    assert "Senior Frontend Engineer" in emp_roles
    assert "Fullstack Engineer" in emp_roles
    assert "Associate Engineer" in emp_roles

    # 5. Projects: exactly 12 projects with 3 mandatory
    projects = db.query(Project).filter(Project.org_id == org.id).all()
    assert len(projects) == 12
    mandatory_projects = [p for p in projects if p.mandatory]
    assert len(mandatory_projects) == 3

    # 6. Roles
    roles = db.query(ProjectRole).filter(ProjectRole.org_id == org.id).all()
    assert len(roles) > 20
    # Confirm some roles have is_stretch_allowed
    stretch_roles = [r for r in roles if r.is_stretch_allowed]
    assert len(stretch_roles) > 0

    # 7. Leaves
    leaves = db.query(EmployeeLeave).filter(EmployeeLeave.org_id == org.id).all()
    assert len(leaves) >= 6
