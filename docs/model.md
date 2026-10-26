# Mathematical Optimization Model: Allocate

This document details the exact mathematical formulation of the constrained optimization engine for the Allocate platform, implemented via **Google OR-Tools CP-SAT**.

---

## 1. Sets and Indices

| Symbol | Definition |
|---|---|
| $e \in E$ | Set of employees |
| $p \in P$ | Set of candidate projects |
| $P_{\text{mand}} \subseteq P$ | Set of mandatory projects |
| $r \in R_p$ | Set of roles demanded by project $p$. Total roles $R = \bigcup_{p \in P} R_p$ |
| $w \in W = \{1, \dots, H\}$ | Set of weekly planning buckets in horizon (default $H = 12$) |
| $s \in S$ | Set of skills in the organization |

---

## 2. Parameters

| Symbol | Description | Default |
|---|---|---|
| $c_e$ | Internal hourly cost of employee $e$ | e.g., \$45 – \$130 |
| $C_e$ | Standard weekly capacity hours for employee $e$ | 40 hours |
| $O_e^{\max}$ | Maximum allowed overtime hours per week for employee $e$ | 10 hours |
| $L_{e,w} \in \{0, 1\}$ | Leave indicator ($1$ if employee $e$ is on leave in week $w$, $0$ otherwise) | Binary |
| $d_{r,w} \in \mathbb{Z}_{\ge 0}$ | Demanded hours for role $r$ in week $w$ ($0$ if outside role date range) | e.g., 40 hours |
| $Rev_p$ | Total contract revenue for project $p$ | \$ |
| $Prio_p \in [1, 5]$ | Strategic priority score for project $p$ | Integer |
| $ReqProf_{r,s} \in [1, 5]$ | Required proficiency level for skill $s$ on role $r$ | Integer |
| $Prof_{e,s} \in [0, 5]$ | Proficiency of employee $e$ in skill $s$ ($0$ if unrated) | Integer |
| $GrowTarget_{e,s} \in [0, 5]$| Growth target of employee $e$ in skill $s$ | Integer |
| $StretchAllowed_r \in \{0, 1\}$ | Whether role $r$ permits stretch staffing | Binary |
| $M_{\text{ratio}}$ | Fraction of mentee's hours deducted from mentor's capacity | 0.10 (10%) |
| $K_{\text{max\_proj}}$ | Maximum concurrent projects an employee can work on in any week | 2 |
| $B_{\min}$ | Minimum assignment block size in hours per week | 10 hours |
| $\rho_{\text{ot}}$ | Penalty cost per hour of overtime | \$50 / hour |

---

## 3. Eligibility & Stretch Definition

An employee $e$ is eligible for role $r$:
- **Standard Qualification:**
  $$\forall s \text{ required by } r: \quad Prof_{e,s} \ge ReqProf_{r,s}$$
- **Stretch Qualification (only if $StretchAllowed_r = 1$):**
  $$\forall s \text{ required by } r: \quad Prof_{e,s} \ge ReqProf_{r,s} - 1 \quad \text{and} \quad \exists s^* \text{ s.t. } Prof_{e,s^*} = ReqProf_{r,s^*} - 1$$

If employee $e$ is staffed on role $r$ as a stretch, a mentor $m \in E \setminus \{e\}$ must be staffed on the same project $p$ with:
$$\forall s \text{ required by } r: \quad Prof_{m,s} \ge ReqProf_{r,s}$$

---

## 4. Decision Variables

| Variable | Domain | Description |
|---|---|---|
| $y_p$ | $\{0, 1\}$ | Binary: $1$ if project $p$ is selected, $0$ otherwise |
| $x_{e,r,w}$ | $\mathbb{Z}_{\ge 0}$ | Integer hours: employee $e$ assigned to role $r$ in week $w$ |
| $a_{e,r}$ | $\{0, 1\}$ | Binary: $1$ if employee $e$ is staffed on role $r$ at any point |
| $overtime_{e,w}$| $\mathbb{Z}_{\ge 0}$ | Integer hours: overtime performed by employee $e$ in week $w$ |
| $z_{e,r}^{\text{stretch}}$ | $\{0, 1\}$ | Binary: $1$ if employee $e$ is in a stretch assignment on role $r$ |
| $mentor_{m,e,r}$ | $\{0, 1\}$ | Binary: $1$ if employee $m$ mentors employee $e$ on role $r$ |

---

## 5. Hard Constraints

### HC-1: Employee Weekly Capacity and Leave
In any week $w$, total working hours plus mentoring commitment must not exceed capacity plus overtime. When an employee is on leave, available hours are zero:
$$\sum_{r \in R} x_{e,r,w} + \sum_{r' \in R, e' \ne e} M_{\text{ratio}} \cdot mentor_{e,e',r'} \cdot x_{e',r',w} \le (C_e + overtime_{e,w}) \cdot (1 - L_{e,w}) \quad \forall e \in E, w \in W$$
$$overtime_{e,w} \le O_e^{\max} \cdot (1 - L_{e,w}) \quad \forall e \in E, w \in W$$

### HC-2: Role Demand Coverage
For any selected project $y_p = 1$, all role hours must be fully staffed across all weeks. If unselected $y_p = 0$, assigned hours must be zero:
$$\sum_{e \in E} x_{e,r,w} = d_{r,w} \cdot y_p \quad \forall p \in P, r \in R_p, w \in W$$

### HC-3: Mandatory Projects
All mandatory projects must be selected:
$$y_p = 1 \quad \forall p \in P_{\text{mand}}$$

### HC-4: Maximum Concurrent Projects & Minimum Block Size
An employee cannot be staffed on scraps of work:
$$B_{\min} \cdot a_{e,r} \le x_{e,r,w} \le d_{r,w} \cdot a_{e,r} \quad \forall e, r, w \text{ where } d_{r,w} > 0$$
In every week $w$, an employee can be active on at most $K_{\text{max\_proj}}$ projects:
$$\sum_{p \in P} \mathbb{I}\left( \sum_{r \in R_p} x_{e,r,w} > 0 \right) \le K_{\text{max\_proj}} \quad \forall e \in E, w \in W$$

### HC-5: Stretch Mentorship Requirement
If an employee $e$ is staffed on a stretch role $r$ ($z_{e,r}^{\text{stretch}} = 1$), there must be exactly one mentor $m$ staffed on the same project $p$:
$$\sum_{m \in QualifiedMentors(r, p)} mentor_{m,e,r} = z_{e,r}^{\text{stretch}} \quad \forall e, r$$
$$\sum_{r' \in R_p} a_{m,r'} \ge mentor_{m,e,r} \quad \forall m, e, r$$

---

## 6. Objective Formulation

The objective maximizes a tunable composite scalar:
$$\max \quad \Omega = \omega_{\text{profit}} \cdot \mathcal{P} + \omega_{\text{growth}} \cdot \mathcal{G} - \omega_{\text{balance}} \cdot \mathcal{B}$$

Where weights satisfy $\omega_{\text{profit}} + \omega_{\text{growth}} + \omega_{\text{balance}} = 1.0$.

### 6.1 Profit Objective ($\mathcal{P}$)
$$\mathcal{P} = \sum_{p \in P} Rev_p \cdot y_p - \sum_{e \in E} \sum_{r \in R} \sum_{w \in W} c_e \cdot x_{e,r,w} - \rho_{\text{ot}} \sum_{e \in E} \sum_{w \in W} overtime_{e,w}$$

### 6.2 Growth Score ($\mathcal{G}$)
Rewards skill development matching employee career aspirations and mentoring:
$$\mathcal{G} = \sum_{e, r, w} \left[ \text{SkillGapClosure}(e, r) \cdot x_{e,r,w} + \text{StretchBonus}(e, r) \cdot z_{e,r}^{\text{stretch}} \right] + \sum_{m, e, r} \text{MentorBonus} \cdot mentor_{m,e,r}$$

Where:
$$\text{SkillGapClosure}(e, r) = \sum_{s \in Skills(r)} \max(0, GrowTarget_{e,s} - Prof_{e,s}) \cdot ReqProf_{r,s}$$

### 6.3 Workload Imbalance Penalty ($\mathcal{B}$)
Penalizes uneven utilization across employees and sustained utilization above 90%:
$$\mathcal{B} = \sum_{e \in E} \sum_{w \in W} \left( \text{DevFromMean}_e + \max(0, \text{Utilization}_{e,w} - 0.90) \cdot 100 \right)$$
