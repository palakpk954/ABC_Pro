import io

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "allocate-api"


def test_auth_login_and_me():
    # Login with seeded admin user
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "alex@acmeconsulting.com", "password": "password123"},
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Call /auth/me with bearer token
    me_resp = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    user_data = me_resp.json()
    assert user_data["email"] == "alex@acmeconsulting.com"
    assert user_data["role"] == "admin"


def test_skills_crud():
    # List skills
    list_resp = client.get(f"{settings.API_V1_STR}/skills")
    assert list_resp.status_code == 200
    skills = list_resp.json()
    assert len(skills) > 0

    # Create new skill
    create_resp = client.post(
        f"{settings.API_V1_STR}/skills",
        json={"name": "Kubernetes Orchestration", "category": "DevOps", "description": "K8s cluster management"},
    )
    assert create_resp.status_code in [201, 400]  # 400 if already created in previous run
    if create_resp.status_code == 201:
        new_sk = create_resp.json()
        assert new_sk["name"] == "Kubernetes Orchestration"


def test_employees_list_and_detail():
    resp = client.get(f"{settings.API_V1_STR}/employees")
    assert resp.status_code == 200
    emps = resp.json()
    assert len(emps) > 0

    first_emp = emps[0]
    detail_resp = client.get(f"{settings.API_V1_STR}/employees/{first_emp['id']}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == first_emp["id"]


def test_projects_list():
    resp = client.get(f"{settings.API_V1_STR}/projects")
    assert resp.status_code == 200
    projs = resp.json()
    assert len(projs) > 0


def test_plan_generate_flow():
    # 1. Generate plan with fast 5s time limit
    gen_resp = client.post(
        f"{settings.API_V1_STR}/plans/generate",
        json={
            "name": "Integration Test Plan",
            "horizon_weeks": 4,
            "slider_value": 0.5,
            "time_limit_seconds": 5.0,
        },
    )
    assert gen_resp.status_code == 201
    plan_data = gen_resp.json()
    plan_id = plan_data["id"]
    assert plan_data["status"] == "draft"
    assert plan_data["horizon_weeks"] == 4
    assert len(plan_data["assignments"]) > 0

    # Verify structured explanations exist
    first_assign = plan_data["assignments"][0]
    assert first_assign["reasons"] is not None

    # 2. Get plan by ID
    get_resp = client.get(f"{settings.API_V1_STR}/plans/{plan_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == plan_id

    # 3. Test Pareto Sweep
    pareto_resp = client.get(f"{settings.API_V1_STR}/plans/{plan_id}/pareto")
    assert pareto_resp.status_code == 200
    pareto_pts = pareto_resp.json()
    assert len(pareto_pts) == 5

    # 4. Test Manual Override
    override_resp = client.post(
        f"{settings.API_V1_STR}/plans/{plan_id}/overrides",
        json={
            "overrides": [
                {
                    "employee_id": first_assign["employee_id"],
                    "project_role_id": first_assign["project_role_id"],
                    "week_number": first_assign["week_number"],
                    "hours": 35,
                    "is_locked": True,
                }
            ]
        },
    )
    assert override_resp.status_code == 200

    # 5. Test Approval Workflow
    approve_resp = client.post(f"{settings.API_V1_STR}/plans/{plan_id}/approve")
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "approved"

    # 6. Test Scenario What-If Diff
    scenario_resp = client.post(
        f"{settings.API_V1_STR}/scenarios",
        json={
            "name": "What-If Employee Absence",
            "base_plan_id": plan_id,
            "modifications": {
                "removed_employee_ids": [first_assign["employee_id"]],
            },
        },
    )
    assert scenario_resp.status_code == 201
    scenario_data = scenario_resp.json()
    assert "diff_summary" in scenario_data
    assert "profit_delta" in scenario_data["diff_summary"]


def test_csv_import_skills():
    csv_payload = "name,category,description\nRust Systems,Backend,Systems programming with Rust\n"
    resp = client.post(
        f"{settings.API_V1_STR}/import/csv/skills",
        files={"file": ("skills.csv", io.BytesIO(csv_payload.encode("utf-8")), "text/csv")},
    )
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["total_rows"] == 1
    assert summary["successful_rows"] == 1


def test_audit_logs():
    resp = client.get(f"{settings.API_V1_STR}/audit")
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) > 0
