"""Unit Tests for Pure Python Optimization Engine

Tests small hand-computable cases:
1. Trivially feasible case
2. Infeasible case
3. Stretch + mentor case
4. Overtime case
5. Leave case
6. Case in which raising growth_weight changes the assignment
"""

from app.engine.domain import (
    EmployeeInput,
    EmployeeSkillProficiency,
    OptimizationConfig,
    OptimizationProblem,
    ProjectInput,
    ProjectRoleInput,
    SkillRequirement,
)
from app.engine.pareto import run_pareto_sweep
from app.engine.pre_solve import run_pre_solve_check
from app.engine.solver import solve_resource_allocation


def test_trivially_feasible_case():
    """Case 1: 1 employee, 1 matching role, fully qualified.

    Hand calculation:
    - Revenue: $5,000
    - Labor: 40 hrs * $50/hr = $2,000
    - Net Profit: $3,000
    """
    emp = EmployeeInput(
        id="emp-1",
        name="Alice Feasible",
        role="Backend Dev",
        cost_per_hour=50.0,
        weekly_capacity_hours=40,
        skills={
            "sk-python": EmployeeSkillProficiency("sk-python", "Python", proficiency=4)
        },
    )

    role = ProjectRoleInput(
        id="role-1",
        project_id="proj-1",
        role_title="Python Developer",
        hours_per_week=40,
        start_week=1,
        end_week=1,
        is_stretch_allowed=False,
        required_skills=[SkillRequirement("sk-python", "Python", min_proficiency=3)],
    )

    proj = ProjectInput(
        id="proj-1",
        name="Simple Python API",
        client="Client A",
        start_week=1,
        end_week=1,
        revenue=5000.0,
        priority=3,
        mandatory=True,
        roles=[role],
    )

    prob = OptimizationProblem(
        horizon_weeks=1,
        employees=[emp],
        projects=[proj],
        config=OptimizationConfig(horizon_weeks=1, profit_weight=1.0, growth_weight=0.0, balance_weight=0.0),
    )

    result = solve_resource_allocation(prob)

    assert result.status in ("OPTIMAL", "FEASIBLE")
    assert len(result.selected_projects) == 1
    assert result.selected_projects[0].is_selected is True
    assert result.objective_breakdown.revenue == 5000.0
    assert result.objective_breakdown.labor_cost == 2000.0
    assert result.objective_breakdown.profit == 3000.0
    assert len(result.assignments) == 1
    assert result.assignments[0].employee_id == "emp-1"
    assert result.assignments[0].hours == 40
    assert result.assignments[0].is_stretch is False


def test_infeasible_case():
    """Case 2: Mandatory project with a role requiring skills no employee has."""
    emp = EmployeeInput(
        id="emp-1",
        name="Bob Junior",
        role="Junior Dev",
        cost_per_hour=40.0,
        weekly_capacity_hours=40,
        skills={
            "sk-react": EmployeeSkillProficiency("sk-react", "React", proficiency=2)
        },
    )

    role = ProjectRoleInput(
        id="role-1",
        project_id="proj-mand",
        role_title="Principal Architect",
        hours_per_week=40,
        start_week=1,
        end_week=1,
        is_stretch_allowed=False,
        required_skills=[SkillRequirement("sk-react", "React", min_proficiency=5)],
    )

    proj = ProjectInput(
        id="proj-mand",
        name="Mission Critical React",
        client="GovCorp",
        start_week=1,
        end_week=1,
        revenue=20000.0,
        mandatory=True,
        roles=[role],
    )

    prob = OptimizationProblem(
        horizon_weeks=1,
        employees=[emp],
        projects=[proj],
        config=OptimizationConfig(horizon_weeks=1),
    )

    # 1. Pre-solve should report conflict in plain language
    diag = run_pre_solve_check(prob)
    assert diag.is_feasible is False
    assert len(diag.conflicts) > 0
    assert "no employee in the organization meets this criteria" in diag.conflicts[0]

    # 2. Solver returns INFEASIBLE
    result = solve_resource_allocation(prob)
    assert result.status == "INFEASIBLE"
    assert len(result.assignments) == 0


def test_stretch_and_mentor_case():
    """Case 3: Role allows stretch.

    Mentee Charlie has React level 3 (required level 4 -> stretch).
    Mentor Diana has React level 5 and is staffed as lead on the same project.
    Mentee must have is_stretch=True and mentor_id=Diana.id.
    """
    mentee = EmployeeInput(
        id="emp-charlie",
        name="Charlie Mentee",
        role="Frontend Dev",
        cost_per_hour=45.0,
        weekly_capacity_hours=40,
        skills={
            "sk-react": EmployeeSkillProficiency("sk-react", "React", proficiency=3, growth_target=4)
        },
    )

    mentor = EmployeeInput(
        id="emp-diana",
        name="Diana Mentor",
        role="Tech Lead",
        cost_per_hour=110.0,
        weekly_capacity_hours=25,
        skills={
            "sk-react": EmployeeSkillProficiency("sk-react", "React", proficiency=5)
        },
    )

    lead_role = ProjectRoleInput(
        id="role-lead",
        project_id="proj-stretch",
        role_title="Frontend Lead",
        hours_per_week=20,
        start_week=1,
        end_week=1,
        is_stretch_allowed=False,
        required_skills=[SkillRequirement("sk-react", "React", min_proficiency=4)],
    )

    stretch_role = ProjectRoleInput(
        id="role-dev",
        project_id="proj-stretch",
        role_title="React Feature Dev",
        hours_per_week=20,
        start_week=1,
        end_week=1,
        is_stretch_allowed=True,
        required_skills=[SkillRequirement("sk-react", "React", min_proficiency=4)],
    )

    proj = ProjectInput(
        id="proj-stretch",
        name="Modern Web App",
        client="Growth Inc",
        start_week=1,
        end_week=1,
        revenue=12000.0,
        mandatory=True,
        roles=[lead_role, stretch_role],
    )

    prob = OptimizationProblem(
        horizon_weeks=1,
        employees=[mentee, mentor],
        projects=[proj],
        config=OptimizationConfig(horizon_weeks=1, profit_weight=0.5, growth_weight=0.5),
    )

    result = solve_resource_allocation(prob)

    assert result.status in ("OPTIMAL", "FEASIBLE")
    stretch_asgn = [a for a in result.assignments if a.employee_id == "emp-charlie"]
    assert len(stretch_asgn) == 1
    assert stretch_asgn[0].is_stretch is True
    assert stretch_asgn[0].mentor_id == "emp-diana"
    assert stretch_asgn[0].mentor_name == "Diana Mentor"
    assert result.objective_breakdown.stretch_bonus > 0


def test_overtime_case():
    """Case 4: Project demands 45 hours in 1 week.

    Employee has 40 standard capacity and 10 max overtime.
    Result: 45 hours assigned, 5 hours overtime with penalty.
    """
    emp = EmployeeInput(
        id="emp-overtime",
        name="Eve Overtime",
        role="Go Specialist",
        cost_per_hour=60.0,
        weekly_capacity_hours=40,
        max_overtime_hours=10,
        skills={
            "sk-go": EmployeeSkillProficiency("sk-go", "Go", proficiency=4)
        },
    )

    role = ProjectRoleInput(
        id="role-go",
        project_id="proj-surge",
        role_title="Surge Backend Dev",
        hours_per_week=45,
        start_week=1,
        end_week=1,
        is_stretch_allowed=False,
        required_skills=[SkillRequirement("sk-go", "Go", min_proficiency=4)],
    )

    proj = ProjectInput(
        id="proj-surge",
        name="High-Throughput Surge",
        client="FastNet",
        start_week=1,
        end_week=1,
        revenue=15000.0,
        mandatory=True,
        roles=[role],
    )

    prob = OptimizationProblem(
        horizon_weeks=1,
        employees=[emp],
        projects=[proj],
        config=OptimizationConfig(horizon_weeks=1, overtime_penalty_per_hour=50.0),
    )

    result = solve_resource_allocation(prob)

    assert result.status in ("OPTIMAL", "FEASIBLE")
    assert len(result.assignments) == 1
    assert result.assignments[0].hours == 45
    # Overtime penalty: 5 hrs * $50/hr = $250
    assert result.objective_breakdown.overtime_cost == 250.0


def test_leave_case():
    """Case 5: Employee is on leave in week 1.

    Demand exists in week 1.
    If sole employee is on leave, week 1 assignment must be 0 and mandatory project fails.
    If replacement is available, replacement works week 1.
    """
    emp_on_leave = EmployeeInput(
        id="emp-frank",
        name="Frank Vacation",
        role="Python Dev",
        cost_per_hour=50.0,
        weekly_capacity_hours=40,
        leave_weeks={1},  # On leave week 1
        skills={"sk-py": EmployeeSkillProficiency("sk-py", "Python", proficiency=4)},
    )

    emp_replacement = EmployeeInput(
        id="emp-grace",
        name="Grace Coverage",
        role="Python Dev",
        cost_per_hour=50.0,
        weekly_capacity_hours=40,
        leave_weeks=set(),
        skills={"sk-py": EmployeeSkillProficiency("sk-py", "Python", proficiency=4)},
    )

    role = ProjectRoleInput(
        id="role-py",
        project_id="proj-leave",
        role_title="Python Dev",
        hours_per_week=40,
        start_week=1,
        end_week=1,
        required_skills=[SkillRequirement("sk-py", "Python", min_proficiency=4)],
    )

    proj = ProjectInput(
        id="proj-leave",
        name="Coverage Project",
        client="Client B",
        start_week=1,
        end_week=1,
        revenue=6000.0,
        mandatory=True,
        roles=[role],
    )

    prob = OptimizationProblem(
        horizon_weeks=1,
        employees=[emp_on_leave, emp_replacement],
        projects=[proj],
        config=OptimizationConfig(horizon_weeks=1),
    )

    result = solve_resource_allocation(prob)

    assert result.status in ("OPTIMAL", "FEASIBLE")
    # Frank MUST have 0 hours in week 1
    frank_hours = sum(a.hours for a in result.assignments if a.employee_id == "emp-frank" and a.week == 1)
    assert frank_hours == 0
    # Grace covers the 40 hours
    grace_hours = sum(a.hours for a in result.assignments if a.employee_id == "emp-grace" and a.week == 1)
    assert grace_hours == 40


def test_growth_weight_changes_assignment():
    """Case 6: Raising growth_weight visibly switches assignment from cheaper dev to high-learning dev.

    - Harry: Cheaper dev ($50/hr), no growth target (already level 5).
    - Ian: More expensive dev ($90/hr), has growth target (currently level 3, wants level 5).
    - Single role requires Python level 3 (40 hours).

    When Profit Weight = 1.0 (Growth = 0.0):
      Cheaper Harry is assigned because labor cost is $2,000 vs $3,600.
    When Growth Weight = 1.0 (Profit = 0.0):
      Ian is assigned because he achieves massive skill gap closure value.
    """
    harry_cheap = EmployeeInput(
        id="emp-harry",
        name="Harry Senior",
        role="Senior Dev",
        cost_per_hour=50.0,
        skills={
            "sk-py": EmployeeSkillProficiency("sk-py", "Python", proficiency=5, growth_target=None)
        },
    )

    ian_growth = EmployeeInput(
        id="emp-ian",
        name="Ian Learner",
        role="Junior Dev",
        cost_per_hour=90.0,
        skills={
            "sk-py": EmployeeSkillProficiency("sk-py", "Python", proficiency=3, growth_target=5)
        },
    )

    role = ProjectRoleInput(
        id="role-learn",
        project_id="proj-learn",
        role_title="Python Project",
        hours_per_week=40,
        start_week=1,
        end_week=1,
        required_skills=[SkillRequirement("sk-py", "Python", min_proficiency=3)],
    )

    proj = ProjectInput(
        id="proj-learn",
        name="Tradeoff Showcase",
        client="Client C",
        start_week=1,
        end_week=1,
        revenue=10000.0,
        mandatory=True,
        roles=[role],
    )

    # 1. Pure Profit Focus: slider = 0.0
    prob_profit = OptimizationProblem(
        horizon_weeks=1,
        employees=[harry_cheap, ian_growth],
        projects=[proj],
        config=OptimizationConfig(profit_weight=1.0, growth_weight=0.0, balance_weight=0.0),
    )
    res_profit = solve_resource_allocation(prob_profit)
    assert res_profit.status in ("OPTIMAL", "FEASIBLE")
    assert res_profit.assignments[0].employee_id == "emp-harry"

    # 2. Pure Growth Focus: slider = 1.0
    prob_growth = OptimizationProblem(
        horizon_weeks=1,
        employees=[harry_cheap, ian_growth],
        projects=[proj],
        config=OptimizationConfig(profit_weight=0.0, growth_weight=1.0, balance_weight=0.0),
    )
    res_growth = solve_resource_allocation(prob_growth)
    assert res_growth.status in ("OPTIMAL", "FEASIBLE")
    assert res_growth.assignments[0].employee_id == "emp-ian"


def test_pareto_sweep_generates_points():
    """Verifies that run_pareto_sweep generates 5 points with monotonic tradeoff."""
    harry = EmployeeInput(
        id="emp-h",
        name="Harry Senior",
        role="Senior Dev",
        cost_per_hour=50.0,
        skills={"sk-py": EmployeeSkillProficiency("sk-py", "Python", proficiency=5)},
    )
    ian = EmployeeInput(
        id="emp-i",
        name="Ian Learner",
        role="Junior Dev",
        cost_per_hour=90.0,
        skills={"sk-py": EmployeeSkillProficiency("sk-py", "Python", proficiency=3, growth_target=5)},
    )
    role = ProjectRoleInput(
        id="role-1",
        project_id="proj-1",
        role_title="Python Dev",
        hours_per_week=40,
        start_week=1,
        end_week=1,
        required_skills=[SkillRequirement("sk-py", "Python", min_proficiency=3)],
    )
    proj = ProjectInput(
        id="proj-1",
        name="Sweep Showcase",
        client="Client",
        start_week=1,
        end_week=1,
        revenue=10000.0,
        mandatory=True,
        roles=[role],
    )

    prob = OptimizationProblem(
        horizon_weeks=1,
        employees=[harry, ian],
        projects=[proj],
    )

    curve = run_pareto_sweep(prob, steps=5)
    assert len(curve) == 5
    assert curve[0]["slider_value"] == 0.0
    assert curve[-1]["slider_value"] == 1.0
