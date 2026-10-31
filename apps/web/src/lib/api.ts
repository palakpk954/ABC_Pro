/**
 * API client and TypeScript interface definitions for Allocate & Living Talent Dossier.
 */

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
  proficiency: number;
  growth_target?: number | null;
}

export interface EmployeeLeave {
  id: string;
  start_date: string;
  end_date: string;
  reason?: string;
}

export interface SkillEvidenceItem {
  skill: string;
  proficiency: number;
  confidence: number;
  evidence: string;
  sources: string[];
}

export interface DossierDocument {
  id: string;
  filename: string;
  file_type: string;
  category: string;
  created_at: string;
}

export interface EmployeeDossier {
  id: string;
  employee_id: string;
  employee_name?: string;
  employee_role?: string;
  employee_email?: string;
  archetype: "Pathfinder" | "Optimizer" | "Firefighter" | "Mentor" | "Generalist" | string;
  archetype_rationale?: string;
  burnout_risk_score: number;
  burnout_factors: string[];
  coaching_sentiment: string;
  client_facing_comfort: string;
  preferred_team_size: string;
  strengths_summary: string[];
  growth_areas: string[];
  career_aspirations: string[];
  stretch_readiness_score: number;
  profile_summary: string;
  confidence_overall: number;
  enrichment_level: number;
  evidence_citations: SkillEvidenceItem[];
  documents: DossierDocument[];
  created_at: string;
  updated_at: string;
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
  end_date?: string;
  career_goals: string[];
  is_active: boolean;
  skills: EmployeeSkill[];
  leaves: EmployeeLeave[];
  dossier?: EmployeeDossier;
}

export interface ProjectRoleSkill {
  id: string;
  skill_id: string;
  skill_name: string;
  required_proficiency: number;
}

export interface ProjectRole {
  id: string;
  project_id?: string;
  role_name?: string;
  role_title?: string;
  hours_per_week: number;
  start_week?: number;
  end_week?: number;
  start_date?: string;
  end_date?: string;
  allow_stretch?: boolean;
  is_stretch_allowed?: boolean;
  skills?: ProjectRoleSkill[];
  skill_requirements?: any[];
}

export interface Project {
  id: string;
  name: string;
  client_name?: string;
  client?: string;
  revenue: number;
  priority: number;
  is_mandatory?: boolean;
  mandatory?: boolean;
  status?: string;
  billing_rate_hourly?: number;
  start_date: string;
  end_date: string;
  roles: ProjectRole[];
}

export interface Assignment {
  id: string;
  employee_id: string;
  employee_name: string;
  project_id: string;
  project_name: string;
  role_id: string;
  role_name: string;
  role_title?: string;
  week_number: number;
  allocated_hours: number;
  hours?: number;
  is_stretch: boolean;
  is_locked?: boolean;
  mentor_id?: string;
  mentor_name?: string;
  hourly_cost: number;
  reasons?: {
    skill_match?: any;
    growth_alignment?: any;
    growth?: any;
    cost?: any;
    mentor_synergy?: any;
    margin_contribution?: any;
    [key: string]: any;
  };
}

export interface Plan {
  id: string;
  name: string;
  status: "draft" | "under_review" | "approved" | "archived" | string;
  horizon_weeks: number;
  tradeoff_slider: number;
  profit_score: number;
  growth_score: number;
  balance_penalty: number;
  dropped_project_reasons?: Record<string, string>;
  objective_breakdown?: {
    profit?: number;
    growth_score?: number;
    revenue?: number;
    labor_cost?: number;
    overtime_cost?: number;
    stretch_bonus?: number;
    balance_penalty?: number;
    [key: string]: any;
  };
  assignments: Assignment[];
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  baseline_plan_id?: string;
  base_plan_id?: string;
  scenario_plan_id?: string;
  modifications?: any;
  diff_summary: {
    profit_diff?: number;
    growth_diff?: number;
    profit_delta?: number;
    growth_delta?: number;
    revenue_delta?: number;
    cost_delta?: number;
    assignments_changed?: number;
    moved_assignments_count?: number;
    unassigned_roles_count?: number;
    projects_added?: number;
    projects_dropped?: number;
    affected_employees?: any[];
    affected_projects?: any[];
    [key: string]: any;
  };
  created_at: string;
}

export interface ParetoPoint {
  slider_value: number;
  profit: number;
  growth: number;
  growth_score?: number;
  label: string;
  status?: string;
  selected_projects_count?: number;
  total_projects_count?: number;
  stretch_assignments_count?: number;
  [key: string]: any;
}

export interface MultiSourceUploadSummary {
  employee_id: string;
  employee_name: string;
  processed_files: string[];
  categories_detected: string[];
  enrichment_level_reached: number;
  confidence_overall: number;
  archetype: string;
  skills_extracted_count: number;
  burnout_risk_score: number;
  message: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API error ${response.status} on ${endpoint}: ${errorBody}`);
  }
  return response.json();
}

/** Upload multi-source files for employee living dossier */
export async function uploadDossierFiles(
  employeeId: string,
  files: File[],
  category = "auto"
): Promise<MultiSourceUploadSummary> {
  const formData = new FormData();
  formData.append("employee_id", employeeId);
  formData.append("category", category);
  files.forEach((f) => formData.append("files", f));

  const response = await fetch(`${API_BASE_URL}/dossier/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Upload failed (${response.status}): ${err}`);
  }

  return response.json();
}

/** Fetch employee living dossier */
export async function getEmployeeDossier(employeeId: string): Promise<EmployeeDossier> {
  return fetchApi<EmployeeDossier>(`/dossier/${employeeId}`);
}

export interface AdvisoryCommercialHealth {
  net_profit: number;
  gross_revenue: number;
  gross_margin_pct: number;
  labor_cost: number;
  overtime_cost: number;
  commercial_rating: string;
}

export interface MentorshipPairing {
  mentee_id: string;
  mentee_name: string;
  mentor_id?: string;
  mentor_name: string;
  coaching_sentiment: string;
  project_name: string;
  role_title: string;
}

export interface FatigueMitigationAlert {
  name: string;
  fatigue_pct: number;
  max_week_hours: number;
  status: string;
  recommendation: string;
}

export interface CognitiveAdvisory {
  plan_id: string;
  plan_name: string;
  advisor_name: string;
  executive_summary: string;
  commercial_health: AdvisoryCommercialHealth;
  people_and_chemistry: {
    active_staff_count: number;
    mentorship_pairings: MentorshipPairing[];
    stretch_assignments: any[];
    archetype_distribution: Record<string, number>;
    fatigue_mitigation_alerts: FatigueMitigationAlert[];
  };
  strategic_recommendations: {
    category: string;
    severity: string;
    title: string;
    detail: string;
  }[];
}

export interface PlanChatCitation {
  source_title: string;
  source_type: string;
  snippet: string;
  confidence?: number;
}

export interface PlanChatResponse {
  answer: string;
  advisor_name: string;
  citations: PlanChatCitation[];
  suggested_followups: string[];
  relevant_employee_ids: string[];
}

/** Fetch cognitive advisory executive commentary for a plan */
export async function getPlanAdvisory(planId: string): Promise<CognitiveAdvisory> {
  return fetchApi<CognitiveAdvisory>(`/plans/${planId}/advisory`);
}

/** Interact with Alex, the cognitive Resource Manager partner */
export async function chatWithAdvisor(
  planId: string,
  query: string,
  history?: { role: string; content: string }[]
): Promise<PlanChatResponse> {
  return fetchApi<PlanChatResponse>(`/plans/${planId}/chat`, {
    method: "POST",
    body: JSON.stringify({ query, history }),
  });
}



export interface ImpactedEngineerChange {
  employee_id: string;
  employee_name: string;
  role_title: string;
  project_name: string;
  previous_hours: number;
  new_hours: number;
  delta_hours: number;
  change_type: "reallocated" | "reduced" | "backfilled" | "added" | string;
  rationale: string;
}

export interface NaturalScenarioSimulateResponse {
  scenario_name: string;
  detected_perturbation: string;
  executive_recommendation: string;
  recommendation_verdict: "Approved" | "Caution" | "Rejected" | string;
  profit_delta: number;
  growth_score_delta: number;
  labor_cost_delta: number;
  overtime_cost_delta: number;
  feasibility_status: string;
  assignments_shifted_count: number;
  impacted_engineers: ImpactedEngineerChange[];
  suggested_mitigations: string[];
}

export interface CandidateComparisonProfile {
  id: string;
  name: string;
  role: string;
  hourly_rate: number;
  archetype: string;
  archetype_fit_rating: "High" | "Moderate" | "Neutral" | string;
  archetype_fit_score: number;
  burnout_risk_score: number;
  burnout_status: string;
  coaching_sentiment: string;
  stretch_readiness_score: number;
  matching_skills: string[];
  evidence_quote?: string;
  weekly_margin_generated: number;
}

export interface CandidateMatchupResponse {
  role_title: string;
  project_name: string;
  candidate_a: CandidateComparisonProfile;
  candidate_b: CandidateComparisonProfile;
  recommended_candidate_id: string;
  verdict_headline: string;
  executive_counterfactual_explanation: string;
  tradeoff_summary: {
    weekly_margin_diff: number;
    burnout_risk_diff: number;
    growth_points_winner: string;
  };
}

/** Simulate a What-If operational perturbation from natural language */
export async function simulateNaturalScenario(
  basePlanId: string,
  prompt: string
): Promise<NaturalScenarioSimulateResponse> {
  return fetchApi<NaturalScenarioSimulateResponse>("/scenarios/simulate-prompt", {
    method: "POST",
    body: JSON.stringify({ base_plan_id: basePlanId, prompt }),
  });
}

/** Fetch counterfactual comparison between two candidate profiles */
export async function getCandidateMatchup(
  employeeIdA: string,
  employeeIdB: string,
  roleTitle: string,
  projectId?: string
): Promise<CandidateMatchupResponse> {
  const query = new URLSearchParams({
    employee_id_a: employeeIdA,
    employee_id_b: employeeIdB,
    role_title: roleTitle,
  });
  if (projectId) query.append("project_id", projectId);
  return fetchApi<CandidateMatchupResponse>(`/employees/compare/matchup?${query.toString()}`);
}
