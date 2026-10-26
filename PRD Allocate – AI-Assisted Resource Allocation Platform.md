# Product Requirements Document: Allocate

*AI-assisted resource allocation and team structuring platform. Working name: "Allocate". Version 0.1 (MVP scope). Status: Draft for review.*

## 1. Overview

Allocate is a decision-support platform that tells a services organization which projects to take on, who should work on each, for how many hours per week, and how each team should be structured. It maximizes profit while explicitly valuing employee learning and growth, with a tunable tradeoff between the two.

The core of the product is a deterministic constrained-optimization engine. Machine learning and LLMs are supporting layers added after the MVP. All outputs are recommendations that a manager reviews, edits, and approves; the system never applies decisions about people automatically.

## 2. Problem Statement

Resource managers and delivery heads in services firms allocate people today using spreadsheets, tribal knowledge, and ad-hoc meetings. This produces:

- Underutilized people on some projects and burnout on others.
- Missed deadlines because skill gaps are discovered late.
- Profitable projects declined, or unprofitable ones accepted, because capacity was never modeled against the whole portfolio.
- Stagnating employees who are repeatedly staffed on the work they already do, which hurts retention.
- No way to quickly answer "what if we lose a key person?" or "what if we win this deal?"

Existing tools (Float, Runn, Resource Guru, Kantata, Planview) mostly visualize and track allocations manually. Few optimize, and almost none treat growth and development as part of the objective.

## 3. Goals and Non-Goals

### 3.1 Goals (MVP)

1. Generate a feasible, optimized staffing plan across a 12-week horizon in under 60 seconds for an organization of up to 500 people and 50 candidate projects.
2. Select the best portfolio of projects given capacity, rather than only assigning people to projects already chosen.
3. Let managers tune the profit-versus-growth tradeoff with a single control and see the resulting tradeoff curve.
4. Explain every assignment and every dropped project in plain language, derived from solver data.
5. Support what-if scenarios with a side-by-side diff against the base plan.
6. Keep the human in control: manual overrides, locked assignments, and an approval workflow with an audit trail.

### 3.2 Non-Goals (MVP)

- Automated, unreviewed application of plans.
- Jira, HRIS, calendar, or Slack integrations (clean extension points only).
- SSO/SAML, billing, and mobile support.
- ML-based effort prediction and LLM features (planned for later releases).
- Performance evaluation, compensation decisions, or any ranking of employees' worth.

## 4. Target Users

**Primary segment:** IT services, consulting, and agencies with 50 to 500 employees. This segment has real staffing complexity, meaningful project-based revenue, and shorter sales cycles than large enterprises.

| Persona | Role | Needs |
| --- | --- | --- |
| Maya, Resource Manager | Owns staffing decisions weekly | Fast, defensible plans; what-if analysis; override control |
| Daniel, Delivery Head | Accountable for margin and delivery | Portfolio-level view, profit impact, risk visibility |
| Priya, Practice or Team Lead | Manages people's development | Visibility into stretch roles, mentoring pairings, growth goals |
| Alex, Admin | Maintains data | Easy CSV import, validation, data hygiene |

Employees are indirect users in the MVP: they do not log in, but their growth goals feed the model.

## 5. User Stories

1. As a resource manager, I can import employees, skills, projects, and roles from CSV so that I can get started without manual entry.
2. As a resource manager, I can generate a 12-week plan and see which projects were selected and which were dropped, with reasons.
3. As a delivery head, I can move a profit-versus-growth slider and see how profit and growth score change.
4. As a resource manager, I can lock specific assignments (for example, a client-requested person) and re-run the plan around them.
5. As a resource manager, I can run a scenario such as "Priya is on leave for four weeks" or "add Project X" and see a diff of who moves and what the profit impact is.
6. As a team lead, I can see which assignments are stretch roles, who mentors them, and which growth targets they serve.
7. As a resource manager, I can manually edit an assignment and be told immediately if it violates a hard constraint.
8. As a delivery head, I can approve or reject a plan, and every change is logged.
9. As an admin, I can see plain-language feasibility problems before running a solve (for example, "Project X needs 2 React experts at level 4; only 1 exists").

## 6. Scope: Functional Requirements

### 6.1 Data Management

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-1 | CRUD for employees (role, cost per hour, weekly capacity, max overtime, availability window, career goals) | P0 |
| FR-2 | CRUD for skills and employee skills (proficiency 1-5, optional growth target 1-5) | P0 |
| FR-3 | CRUD for projects (client, dates, revenue, priority 1-5, mandatory flag, status) | P0 |
| FR-4 | CRUD for project roles (required skills with minimum proficiency, hours per week, dates, stretch allowed flag) | P0 |
| FR-5 | CRUD for leave and unavailability by date range | P0 |
| FR-6 | CSV import for employees, skills, projects, and roles with row-level validation errors | P0 |
| FR-7 | Multi-tenancy: every record scoped by org; basic JWT authentication | P0 |

### 6.2 Optimization Engine

The engine is a pure Python module with typed inputs and outputs, independent of web and database layers, using Google OR-Tools CP-SAT.

**Decision variables**

- Project selected (binary) per project.
- Hours worked per employee, role, and week (integer).
- Employee staffed on role (binary), used to limit fragmentation.
- Overtime hours per employee and week (integer, nonnegative).

**Eligibility.** An employee is eligible for a role if they meet every required skill at the required proficiency. If the role allows stretch, proficiency one level below is acceptable; such an assignment is flagged as a stretch and requires a qualified mentor on the same project.

**Hard constraints**

| ID | Constraint |
| --- | --- |
| HC-1 | Weekly hours per employee do not exceed capacity plus overtime; overtime does not exceed the employee's maximum; zero hours during leave |
| HC-2 | Every selected project's roles are fully staffed for every week of the project; unselected projects receive zero hours |
| HC-3 | Mandatory projects must be selected; if infeasible, report the conflicting constraints |
| HC-4 | Maximum concurrent projects per employee (default 2) |
| HC-5 | Minimum assignment block size to avoid scraps of work (configurable) |
| HC-6 | Stretch assignments require a mentor at or above the required proficiency; mentoring time (default 10% of the mentee's hours) counts against the mentor's capacity |

**Objective (maximize), with weights configurable per plan**

- **Profit:** project revenue of selected projects, minus labor cost, minus an overtime penalty.
- **Growth score:** value of closing skill gaps that match employee growth targets, stretch bonus, mentoring bonus, minus a penalty for repeating identical work too long.
- **Balance:** a penalty for utilization variance across employees and for sustained utilization above 90%.

Total = profit weight × profit + growth weight × growth score − balance weight × imbalance. A single slider (0 to 1) maps to these weights in the UI, and all components are returned separately.

**Solver behavior**

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-8 | Time limit (default 30 seconds); return the best solution found and the optimality gap | P0 |
| FR-9 | Pre-solve feasibility check with plain-language conflict messages | P0 |
| FR-10 | Pareto sweep: solve at five growth-weight settings and return the profit-versus-growth curve | P0 |
| FR-11 | Locked assignments honored as fixed inputs | P0 |
| FR-12 | Reproducibility: fixed random seed and logged input hash | P0 |
| FR-13 | Log solver statistics (variables, constraints, wall time, gap) | P1 |

### 6.3 Plans, Scenarios, and Governance

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-14 | Versioned plans with status: draft, approved, rejected | P0 |
| FR-15 | Scenarios: remove an employee for a date range, add a project, change a role's requirements, change weights; each produces a new plan plus a diff against the base | P0 |
| FR-16 | Manual override of assignments with re-validation of hard constraints and re-scoring | P0 |
| FR-17 | Approve and reject actions, restricted by role | P0 |
| FR-18 | Audit log for every state change (who, what, when, before and after) | P0 |

### 6.4 Explainability

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-19 | Per-assignment structured reasons: skill match, cost, growth contribution, stretch and mentor flags | P0 |
| FR-20 | Per-dropped-project reason: insufficient capacity, skill gap, or lower value than the alternatives it displaced, derived from counterfactual re-solves | P0 |
| FR-21 | Explanations are generated from solver data, not by an LLM, in the MVP | P0 |

### 6.5 User Interface

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-22 | Dashboard: utilization heatmap (people by weeks), selected versus dropped projects, profit and growth score cards | P0 |
| FR-23 | Data pages: employees, skills matrix, projects and roles, with inline edit and CSV import | P0 |
| FR-24 | Plan view: timeline grid by employee or by project, with stretch and mentor badges; click an assignment for its explanation | P0 |
| FR-25 | Controls: profit-versus-growth slider, lock toggle, generate button with progress, Pareto chart | P0 |
| FR-26 | Scenario panel with side-by-side diff (profit delta, growth delta, who moved) | P0 |
| FR-27 | Empty, loading, and error states; keyboard accessible; designed for 1280px and wider | P0 |

## 7. Non-Functional Requirements

- **Performance:** a plan for 500 people and 50 projects over 12 weeks returns a good solution within 60 seconds; the UI remains responsive while jobs run asynchronously.
- **Reliability:** the solver always returns either a feasible plan or a clear explanation of infeasibility.
- **Security:** tenant isolation on every query; no secrets in code; passwords hashed; JWT expiry and refresh. SSO is a documented follow-up.
- **Privacy:** employee data is minimized to what the model needs; growth goals are visible only to authorized roles.
- **Auditability:** all plan state changes are logged and immutable.
- **Maintainability:** typed code, linting, a modular monolith, and documentation of the mathematical model matching the implementation.
- **Accessibility:** keyboard navigation and sufficient contrast in the core flows.

## 8. Technical Approach (Summary)

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic.
- **Optimization:** Google OR-Tools CP-SAT.
- **Database:** PostgreSQL.
- **Frontend:** Next.js, TypeScript, Tailwind, shadcn/ui, TanStack Query, Recharts.
- **Async jobs:** FastAPI background tasks behind an interface that Celery or Temporal can replace.
- **Dev and delivery:** Docker Compose, Makefile, CI, pytest, Vitest, Playwright.

## 9. Responsible AI and Compliance

This product informs decisions about people's work and development, which makes it sensitive and, in the EU, potentially high-risk under the EU AI Act.

- Recommendations only: a named human approves every plan.
- Transparency: every recommendation includes its reasons and the weights used.
- Fairness: track and report distribution of stretch opportunities, hours, and growth value across employee groups where data permits (post-MVP report, with data model prepared now).
- No use for performance rating, compensation, or termination decisions; this is stated in the product terms.
- Employees' growth goals are optional inputs and can be removed.

## 10. Success Metrics

**Product (pilot, 90 days)**

- At least 60% of generated plans are approved with edits to fewer than 20% of assignments.
- Time to produce a staffing plan reduced by at least 50% versus the pilot's current process.
- Median time from data import to first plan under 30 minutes.

**Business outcomes (measured with pilot customers)**

- Billable utilization improvement of 3 to 5 points without a rise in overtime.
- Reduction in the number of unstaffed project weeks.
- Increase in the share of employees with at least one assignment aligned to a growth goal.

**Engine quality**

- 100% of returned plans satisfy all hard constraints (verified by an independent validator).
- Median optimality gap below 5% within the time limit on benchmark data.

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Poor skill data quality | Bad plans erode trust | Skills matrix editor, import validation, flag stale skill data, later LLM-based skill extraction |
| Unreliable effort estimates | Plans break in execution | Model uncertainty later with ML; allow buffer parameters now |
| Crowded market | Slow adoption | Narrow wedge: services firms, portfolio selection plus growth-aware optimization |
| Solver time at scale | Poor user experience | Time limits, warm starts, problem decomposition by horizon or practice, asynchronous jobs |
| User distrust of black-box output | Low adoption | Explanations, overrides, locks, and what-if analysis |
| Regulatory exposure | Legal and reputational | Human-in-the-loop design, audit trail, fairness reporting |
| Scope creep | Missed MVP | Strict non-goals list and phased delivery |

## 12. Release Plan

| Phase | Deliverable | Exit criteria |
| --- | --- | --- |
| 0 | Repo scaffold, Docker Compose, schema, migrations, seed script | `make up` and `make seed` work |
| 1 | Optimization module, unit tests, CLI against seed data | All hand-computed test cases pass; plan and objective breakdown printed |
| 2 | API: CRUD, import, plan generation, scenarios, overrides, approvals, audit log | Integration tests pass |
| 3 | Frontend: data pages, plan view, slider, scenario diff, Pareto chart | Smoke test passes end to end |
| 4 | Explanations, feasibility diagnostics, polish, documentation | Pilot-ready build |

## 13. Roadmap Beyond the MVP

1. Integrations: Jira, Google Calendar, Slack, and HRIS through a unified API.
2. ML layer: effort estimation with uncertainty, project success probability, skill inference.
3. LLM layer: natural-language what-if queries, plain-English explanations, skill extraction from resumes and tickets.
4. Enterprise: SSO/SAML, advanced RBAC, fairness reports, SOC 2 readiness.
5. Robust optimization: plans that remain feasible under estimation error and attrition.
6. Pipeline-aware planning: probability-weighted incoming deals.

## 14. Open Questions

1. Is revenue modeled as fixed price per project, billing rate times hours, or both? (The MVP assumes both are supported.)
2. How should growth value be calibrated: by a fixed formula, or by manager-defined weights per skill?
3. Should employees see their own growth recommendations in a later release?
4. What is the right default for overtime penalty and maximum utilization in the target segment?
5. Which pilot customers and how many will validate the model before the integrations phase?
6. What data-residency requirements will the first customers impose?

## 15. Glossary

- **Stretch assignment:** a role filled by someone one proficiency level below the requirement, supported by a mentor.
- **Pareto sweep:** a set of solves at different weightings that shows the best achievable tradeoffs between profit and growth.
- **Scenario:** a plan generated with modified inputs for what-if comparison.
- **Optimality gap:** the distance between the best solution found and the proven upper bound.
