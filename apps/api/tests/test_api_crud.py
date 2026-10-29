from app.models import Organization, User, UserRole
from app.core.security import create_access_token


def test_skills_crud_api(client, auth_headers):
    # 1. Create Skill
    create_res = client.post(
        "/api/v1/skills",
        json={"name": "Kubernetes", "category": "DevOps", "description": "K8s cluster management"},
        headers=auth_headers,
    )
    assert create_res.status_code == 201
    skill_data = create_res.json()
    skill_id = skill_data["id"]
    assert skill_data["name"] == "Kubernetes"

    # 2. List Skills
    list_res = client.get("/api/v1/skills", headers=auth_headers)
    assert list_res.status_code == 200
    skills = list_res.json()
    assert any(s["id"] == skill_id for s in skills)

    # 3. Update Skill
    update_res = client.put(
        f"/api/v1/skills/{skill_id}",
        json={"description": "Updated K8s description"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["description"] == "Updated K8s description"

    # 4. Delete Skill
    del_res = client.delete(f"/api/v1/skills/{skill_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 5. Verify deleted
    get_res = client.get(f"/api/v1/skills/{skill_id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_employees_and_subresources_crud_api(client, auth_headers):
    # Create skill first
    skill_res = client.post(
        "/api/v1/skills",
        json={"name": "FastAPI", "category": "Backend"},
        headers=auth_headers,
    )
    skill_id = skill_res.json()["id"]

    # 1. Create Employee
    emp_res = client.post(
        "/api/v1/employees",
        json={
            "name": "Jordan Lee",
            "email": "jordan.lee@example.com",
            "role": "Backend Engineer",
            "cost_per_hour": 75.0,
            "weekly_capacity_hours": 40,
            "max_overtime_hours": 10,
            "start_date": "2026-01-01",
            "career_goals": ["FastAPI", "System Design"],
        },
        headers=auth_headers,
    )
    assert emp_res.status_code == 201
    emp_id = emp_res.json()["id"]

    # 2. Assign Skill
    emp_skill_res = client.post(
        f"/api/v1/employees/{emp_id}/skills",
        json={"skill_id": skill_id, "proficiency": 4, "growth_target": 5},
        headers=auth_headers,
    )
    assert emp_skill_res.status_code == 201
    assert emp_skill_res.json()["proficiency"] == 4

    # 3. Add Leave
    leave_res = client.post(
        f"/api/v1/employees/{emp_id}/leaves",
        json={"start_date": "2026-11-09", "end_date": "2026-11-20", "reason": "Annual leave"},
        headers=auth_headers,
    )
    assert leave_res.status_code == 201
    assert leave_res.json()["reason"] == "Annual leave"

    # 4. Get Employee with nested skills and leaves
    get_res = client.get(f"/api/v1/employees/{emp_id}", headers=auth_headers)
    assert get_res.status_code == 200
    emp_full = get_res.json()
    assert len(emp_full["skills"]) == 1
    assert len(emp_full["leaves"]) == 1


def test_projects_and_roles_crud_api(client, auth_headers):
    # Create skill
    skill_res = client.post(
        "/api/v1/skills",
        json={"name": "Go", "category": "Backend"},
        headers=auth_headers,
    )
    skill_id = skill_res.json()["id"]

    # Create Project with Role
    proj_res = client.post(
        "/api/v1/projects",
        json={
            "name": "Microservices Migration",
            "client": "Acme Corp",
            "start_date": "2026-11-02",
            "end_date": "2027-01-22",
            "revenue": 140000.0,
            "priority": 4,
            "mandatory": True,
            "roles": [
                {
                    "role_title": "Go Architect",
                    "hours_per_week": 40,
                    "start_date": "2026-11-02",
                    "end_date": "2027-01-22",
                    "is_stretch_allowed": False,
                    "skills": [{"skill_id": skill_id, "min_proficiency": 4}],
                }
            ],
        },
        headers=auth_headers,
    )
    assert proj_res.status_code == 201
    proj_data = proj_res.json()
    assert proj_data["mandatory"] is True
    assert len(proj_data["roles"]) == 1
    assert proj_data["roles"][0]["role_title"] == "Go Architect"


def test_multi_tenant_api_isolation(client, db, test_org, auth_headers):
    # Create another tenant org and user
    other_org = Organization(name="Other Tenant Corp")
    db.add(other_org)
    db.commit()

    other_user = User(
        org_id=other_org.id,
        email="other@othertenant.com",
        full_name="Other User",
        role=UserRole.RESOURCE_MANAGER,
        hashed_password="hash",
    )
    db.add(other_user)
    db.commit()

    other_token = create_access_token(other_user.id, other_org.id, other_user.role.value)
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # Org 1 creates skill
    s1_res = client.post("/api/v1/skills", json={"name": "Org1 Skill", "category": "General"}, headers=auth_headers)
    assert s1_res.status_code == 201
    s1_id = s1_res.json()["id"]

    # Org 2 lists skills -> should NOT see Org 1 skill
    org2_skills_res = client.get("/api/v1/skills", headers=other_headers)
    assert org2_skills_res.status_code == 200
    assert not any(s["id"] == s1_id for s in org2_skills_res.json())

    # Org 2 attempts to get Org 1 skill directly -> 404
    get_res = client.get(f"/api/v1/skills/{s1_id}", headers=other_headers)
    assert get_res.status_code == 404
