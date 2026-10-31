// API Client & Type Definitions for Allocate Web

export interface Skill {
  id: string;
  name: string;
  category: string;
  description?: string;
}

export interface EmployeeSkill {
  id: string;
  skill_id: string;
  skill_name: string;
  skill_category?: string;
  proficiency: number;
  growth_target?: number | null;
}

export interface EmployeeLeave {
  id: string;
  start_date: string;
  end_date: string;
  reason?: string;
}

export interface Employee {
  id: string;
  name: string;
  email: string;
  role: string;
  cost_per_hour: number;
  weekly_capacity_hours: number;
  max_overtime_hours: number;
  start_date: string;
  end_date?: string | null;
  career_goals: string[];
  is_active: boolean;
  skills: EmployeeSkill[];
  leaves: EmployeeLeave[];
}

export interface ProjectRoleSkill {
  id: string;
  skill_id: string;
  skill_name?: string;
  min_proficiency: number;
}

export interface ProjectRole {
  id: string;
  project_id: string;
  role_title: string;
  hours_per_week: number;
  start_date: string;
  end_date: string;
  is_stretch_allowed: boolean;
  skill_requirements: ProjectRoleSkill[];
}

export interface Project {
  id: string;
  name: string;
  client: string;
  start_date: string;
  end_date: string;
  revenue: number;
  billing_rate_hourly?: number | null;
  priority: number;
  mandatory: boolean;
  status: string;
  roles: ProjectRole[];
}

export interface AssignmentReason {
  skill_match?: {
    employee_proficiency: number;
    required_proficiency: number;
    skills: string[];
  };
  stretch?: {
    is_stretch: boolean;
    mentor_id?: string;
    mentor_name?: string;
    mentor_hours?: number;
  };
  growth?: {
    growth_score_contribution: number;
    matched_goals?: string[];
  };
  cost?: {
    hourly_cost: number;
    total_assignment_cost: number;
  };
}

export interface Assignment {
  id: string;
  employee_id: string;
  employee_name?: string;
  project_id?: string;
  project_name?: string;
  project_role_id: string;
  role_title?: string;
  week_number: number;
  hours: number;
  is_stretch: boolean;
  mentor_id?: string | null;
  mentor_name?: string | null;
  is_locked: boolean;
  reasons?: AssignmentReason;
}

export interface Plan {
  id: string;
  name: string;
  status: "draft" | "approved" | "rejected";
  horizon_weeks: number;
  start_date: string;
  profit_weight: number;
  growth_weight: number;
  balance_weight: number;
  total_score?: number;
  profit_score?: number;
  growth_score?: number;
  balance_penalty?: number;
  solver_status?: string;
  solver_gap?: number;
  solver_wall_time_ms?: number;
  objective_breakdown?: {
    revenue?: number;
    labor_cost?: number;
    overtime_cost?: number;
    profit?: number;
    skill_growth?: number;
    stretch_bonus?: number;
    mentoring_bonus?: number;
    growth_score?: number;
    utilization_imbalance_penalty?: number;
    sustained_overutilization_penalty?: number;
    balance_penalty?: number;
  };
  dropped_project_reasons?: Record<string, string>;
  created_at: string;
  updated_at: string;
  assignments: Assignment[];
}

export interface ParetoPoint {
  slider_value: number;
  profit_weight: number;
  growth_weight: number;
  profit: number;
  growth_score: number;
  revenue: number;
  labor_cost: number;
  overtime_cost: number;
  selected_projects_count: number;
  total_projects_count: number;
  stretch_assignments_count: number;
  status: string;
  optimality_gap: number;
}

export interface Scenario {
  id: string;
  base_plan_id: string;
  modified_plan_id?: string;
  name: string;
  description?: string;
  modifications: Record<string, any>;
  diff_summary?: {
    profit_delta: number;
    growth_delta: number;
    revenue_delta?: number;
    cost_delta?: number;
    moved_assignments_count: number;
    unassigned_roles_count: number;
    affected_employees: string[];
    affected_projects: string[];
  };
  created_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function loginAsPersona(email: string, password = "password123"): Promise<boolean> {
  if (typeof window === "undefined") return false;
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.access_token) {
        localStorage.setItem("allocate_token", data.access_token);
        localStorage.setItem("allocate_user", JSON.stringify(data));
        return true;
      }
    }
  } catch (err) {
    console.warn("Login failed:", err);
  }
  return false;
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  let token = typeof window !== "undefined" ? localStorage.getItem("allocate_token") : null;

  // Auto-authenticate with seeded admin persona if no token present
  if (!token && typeof window !== "undefined") {
    try {
      const loginRes = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "maya@acmeconsulting.com", password: "password123" }),
      });
      if (loginRes.ok) {
        const data = await loginRes.json();
        token = data.access_token;
        if (token) {
          localStorage.setItem("allocate_token", token);
          localStorage.setItem("allocate_user", JSON.stringify(data));
        }
      }
    } catch {}
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {}
    throw new Error(errorDetail);
  }

  return response.json();
}
