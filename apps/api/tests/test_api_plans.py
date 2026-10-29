from datetime import date
from app.models import (
    Employee,
    EmployeeSkill,
    Project,
    ProjectRole,
    ProjectRoleSkill,
    Skill,
)
from app.services.plan_service import execute_plan_generation
from app.engine.domain import OptimizationConfig


def setup_minimal_firm_data(db, org_id):
    """Sets up minimal feasible firm data for fast plan generation tests."""
    py_skill = Skill(org_id=org_id, name="Python", category="Backend")
    react_skill = Skill(org_id=org_id, name="React", category="Frontend")
    db.add_all([py_skill, react_skill])
    db.commit()

    emp1 = Employee(
        org_id=org_id,
        name="Senior Alice",
        email="alice@testfirm.com",
        role="Senior Dev",
        cost_per_hour=70.0,
        weekly_capacity_hours=40,
        max_overtime_hours=10,
        start_date=date(2026, 1, 1),
    )
    emp2 = Employee(
        org_id=org_id,
        name="Junior Bob",
        email="bob@testfirm.com",
        role="Junior Dev",
        cost_per_hour=40.0,
        weekly_capacity_hours=40,
        max_overtime_hours=10,
        start_date=date(2026, 1, 1),
    )
    db.add_all([emp1, emp2])
    db.commit()

    # Alice has Python 5, React 4
    # Bob has Python 3 (growth target 5), React 2
    es1 = EmployeeSkill(org_id=org_id, employee_id=emp1.id, skill_id=py_skill.id, proficiency=5)
    es2 = EmployeeSkill(org_id=org_id, employee_id=emp1.id, skill_id=react_skill.id, proficiency=4)
    es3 = EmployeeSkill(org_id=org_id, employee_id=emp2.id, skill_id=py_skill.id, proficiency=3, growth_target=5)
    es4 = EmployeeSkill(org_id=org_id, employee_id=emp2.id, skill_id=react_skill.id, proficiency=2)
    db.add_all([es1, es2, es3, es4])
    db.commit()

    # Project 1: Mandatory Python API
    p1 = Project(
        org_id=org_id,
        name="Fintech API",
        client="FinTech",
        start_date=date(2026, 11, 2),
        end_date=date(2026, 11, 15),
        revenue=10000.0,
        mandatory=True,
    )
    db.add(p1)
    db.commit()

    r1 = ProjectRole(
        org_id=org_id,
        project_id=p1.id,
        role_title="Lead Dev",
        hours_per_week=40,
        start_date=date(2026, 11, 2),
        end_date=date(2026, 11, 15),
    )
    db.add(r1)
    db.commit()

    prs1 = ProjectRoleSkill(org_id=org_id, project_role_id=r1.id, skill_id=py_skill.id, min_proficiency=3)
    db.add(prs1)
    db.commit()

    return {"emp1": emp1, "emp2": emp2, "p1": p1, "r1": r1, "py_skill": py_skill}


def test_plan_generation_and_retrieval(client, db, test_org, auth_headers):
    setup_minimal_firm_data(db, test_org.id)

    # 1. Trigger generate endpoint
    gen_res = client.post(
        "/api/v1/plans/generate",
        json={"name": "Sprint 1 Plan", "horizon_weeks": 2, "slider_value": 0.5, "solver_time_limit_seconds": 10.0},
        headers=auth_headers,
    )
    assert gen_res.status_code == 202
    data = gen_res.json()
    assert "job_id" in data
    assert "plan_id" in data
    plan_id = data["plan_id"]

    # Execute synchronous generation for test verification
    execute_plan_generation(
        plan_id=plan_id,
        org_id=test_org.id,
        user_id="test-user",
        config=OptimizationConfig(horizon_weeks=2, time_limit_seconds=5.0),
        locked_assignments=[],
        db=db,
    )

    # 2. Get Plan
    get_res = client.get(f"/api/v1/plans/{plan_id}", headers=auth_headers)
    assert get_res.status_code == 200
    plan_full = get_res.json()
    assert plan_full["id"] == plan_id
    assert plan_full["status"] == "draft"
    assert plan_full["profit_score"] is not None
    assert len(plan_full["assignments"]) > 0


def test_assignment_override_validation(client, db, test_org, auth_headers):
    data = setup_minimal_firm_data(db, test_org.id)
    emp1 = data["emp1"]
    emp2 = data["emp2"]

    # Generate plan
    gen_res = client.post(
        "/api/v1/plans/generate",
        json={"name": "Override Plan", "horizon_weeks": 2},
        headers=auth_headers,
    )
    plan_id = gen_res.json()["plan_id"]
    execute_plan_generation(
        plan_id=plan_id,
        org_id=test_org.id,
        user_id="test-user",
        config=OptimizationConfig(horizon_weeks=2, time_limit_seconds=5.0),
        locked_assignments=[],
        db=db,
    )

    plan = client.get(f"/api/v1/plans/{plan_id}", headers=auth_headers).json()
    asgn = plan["assignments"][0]

    # Valid override: reassign to Bob (who meets Python 3)
    override_res = client.patch(
        f"/api/v1/plans/{plan_id}/assignments",
        json={"assignment_id": asgn["id"], "employee_id": emp2.id, "hours": 40, "is_locked": True},
        headers=auth_headers,
    )
    assert override_res.status_code == 200
    assert override_res.json()["employee_id"] == emp2.id

    # Invalid override: capacity violation (hours > 50)
    invalid_res = client.patch(
        f"/api/v1/plans/{plan_id}/assignments",
        json={"assignment_id": asgn["id"], "employee_id": emp2.id, "hours": 65, "is_locked": True},
        headers=auth_headers,
    )
    assert invalid_res.status_code == 400
    assert "exceeds maximum capacity" in invalid_res.json()["detail"]


def test_scenario_creation_and_diff(client, db, test_org, auth_headers):
    setup_minimal_firm_data(db, test_org.id)

    gen_res = client.post("/api/v1/plans/generate", json={"horizon_weeks": 2}, headers=auth_headers)
    plan_id = gen_res.json()["plan_id"]
    execute_plan_generation(
        plan_id=plan_id,
        org_id=test_org.id,
        user_id="test-user",
        config=OptimizationConfig(horizon_weeks=2, time_limit_seconds=5.0),
        locked_assignments=[],
        db=db,
    )

    # Create Scenario
    scen_res = client.post(
        f"/api/v1/plans/{plan_id}/scenarios",
        json={
            "name": "Higher Growth Scenario",
            "description": "Shift focus towards learning targets",
            "modifications": {"slider_value": 0.9},
        },
        headers=auth_headers,
    )
    assert scen_res.status_code == 201
    scen_data = scen_res.json()
    assert scen_data["base_plan_id"] == plan_id
    assert "diff_summary" in scen_data
    assert "profit_delta" in scen_data["diff_summary"]


def test_plan_governance_approvals(client, db, test_org, auth_headers, delivery_head_headers):
    setup_minimal_firm_data(db, test_org.id)

    gen_res = client.post("/api/v1/plans/generate", json={"horizon_weeks": 2}, headers=auth_headers)
    plan_id = gen_res.json()["plan_id"]
    execute_plan_generation(
        plan_id=plan_id,
        org_id=test_org.id,
        user_id="test-user",
        config=OptimizationConfig(horizon_weeks=2, time_limit_seconds=5.0),
        locked_assignments=[],
        db=db,
    )

    # 1. Resource Manager cannot approve (403 Forbidden)
    rm_approve_res = client.post(f"/api/v1/plans/{plan_id}/approve", headers=auth_headers)
    assert rm_approve_res.status_code == 403

    # 2. Delivery Head can approve (200 OK)
    dh_approve_res = client.post(f"/api/v1/plans/{plan_id}/approve", headers=delivery_head_headers)
    assert dh_approve_res.status_code == 200
    assert dh_approve_res.json()["status"] == "approved"

    # 3. Delivery Head can reject
    dh_reject_res = client.post(f"/api/v1/plans/{plan_id}/reject", headers=delivery_head_headers)
    assert dh_reject_res.status_code == 200
    assert dh_reject_res.json()["status"] == "rejected"


def test_pareto_endpoint(client, db, test_org, auth_headers):
    setup_minimal_firm_data(db, test_org.id)

    gen_res = client.post("/api/v1/plans/generate", json={"horizon_weeks": 2}, headers=auth_headers)
    plan_id = gen_res.json()["plan_id"]

    pareto_res = client.get(f"/api/v1/plans/{plan_id}/pareto", headers=auth_headers)
    assert pareto_res.status_code == 200
    curve_data = pareto_res.json()
    assert curve_data["plan_id"] == plan_id
    assert len(curve_data["curve"]) == 5
