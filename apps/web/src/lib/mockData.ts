/**
 * Realistic seed and mock data for Allocate platform & Living Talent Dossiers.
 */

import { Employee, Project, Skill, Plan, Scenario, ParetoPoint, CognitiveAdvisory } from "./api";

export const MOCK_SKILLS: Skill[] = [
  { id: "sk-1", name: "React", category: "Frontend", description: "Modern React with hooks and state management" },
  { id: "sk-2", name: "TypeScript", category: "Frontend", description: "Typed JavaScript development" },
  { id: "sk-3", name: "Python", category: "Backend", description: "Python 3, async programming, data manipulation" },
  { id: "sk-4", name: "FastAPI", category: "Backend", description: "High-performance async Python APIs" },
  { id: "sk-5", name: "PostgreSQL", category: "Data", description: "Relational database schema and optimization" },
  { id: "sk-6", name: "Docker", category: "DevOps", description: "Container lifecycle and deployment" },
  { id: "sk-7", name: "Kubernetes", category: "DevOps", description: "Cloud-native container orchestration" },
  { id: "sk-8", name: "Distributed Systems", category: "Architecture", description: "Microservices and event streams" },
  { id: "sk-9", name: "Machine Learning", category: "AI/ML", description: "PyTorch, model serving, and RAG" },
  { id: "sk-10", name: "UI/UX Design", category: "Design", description: "Figma design systems and user journey" },
];

export const MOCK_EMPLOYEES: Employee[] = [
  {
    id: "emp-1",
    name: "Sarah Chen",
    email: "sarah.chen@acme.com",
    role: "Principal Cloud Architect",
    cost_per_hour: 125,
    weekly_capacity_hours: 40,
    max_overtime_hours: 10,
    start_date: "2024-01-15",
    career_goals: ["Transitioning / mastering Rust", "Stepping into Engineering VP"],
    is_active: true,
    skills: [
      { id: "es-1", skill_id: "sk-3", skill_name: "Python", proficiency: 5, growth_target: 5 },
      { id: "es-2", skill_id: "sk-4", skill_name: "FastAPI", proficiency: 5, growth_target: 5 },
      { id: "es-3", skill_id: "sk-7", skill_name: "Kubernetes", proficiency: 4, growth_target: 5 },
      { id: "es-4", skill_id: "sk-8", skill_name: "Distributed Systems", proficiency: 5, growth_target: 5 },
    ],
    leaves: [],
    dossier: {
      id: "dos-1",
      employee_id: "emp-1",
      employee_name: "Sarah Chen",
      employee_role: "Principal Cloud Architect",
      employee_email: "sarah.chen@acme.com",
      archetype: "Pathfinder",
      archetype_rationale: "Demonstrates exceptional ability to design 0-to-1 architectures under extreme ambiguity.",
      burnout_risk_score: 0.22,
      burnout_factors: ["Consistent high performance with sustainable workload balance"],
      coaching_sentiment: "Exemplary Coach & Mentor (High Multiplier)",
      client_facing_comfort: "High (Confident in front of enterprise clients & executives)",
      preferred_team_size: "Focused strike team (2-4 members)",
      strengths_summary: [
        "High-throughput API development & async design",
        "System architecture & decoupled service boundaries",
        "Praised for patient coaching of junior engineers"
      ],
      growth_areas: ["Expanding deep systems programming in Rust"],
      career_aspirations: ["Leading enterprise distributed cloud transformation", "Mentoring the next generation of architects"],
      stretch_readiness_score: 0.95,
      profile_summary: "Living Dossier synthesized from Resume, Q3 Review, and 360 Peer Feedback. Key strengths in Distributed Systems and Python with 96% confidence.",
      confidence_overall: 0.96,
      enrichment_level: 2,
      evidence_citations: [
        {
          skill: "Python",
          proficiency: 5,
          confidence: 0.98,
          evidence: "Led core rewrite of data ingestion engine in Q3; reduced P99 latency by 45%. Praised in 360 feedback.",
          sources: ["resume", "performance_report", "feedback_360"]
        },
        {
          skill: "Distributed Systems",
          proficiency: 5,
          confidence: 0.95,
          evidence: "Architected event-driven microservices processing 120k msgs/sec on Kafka.",
          sources: ["resume", "performance_report"]
        },
        {
          skill: "Kubernetes",
          proficiency: 4,
          confidence: 0.91,
          evidence: "Managed automated multi-region failover and Helm deployments across 4 clusters.",
          sources: ["performance_report"]
        }
      ],
      documents: [
        { id: "doc-1", filename: "sarah_chen_resume.pdf", file_type: "pdf", category: "resume", created_at: "2026-09-10T10:00:00Z" },
        { id: "doc-2", filename: "q3_2026_performance_review.docx", file_type: "docx", category: "performance_report", created_at: "2026-10-15T14:30:00Z" },
        { id: "doc-3", filename: "peer_360_feedback_oct.txt", file_type: "text", category: "feedback_360", created_at: "2026-10-22T09:15:00Z" }
      ],
      created_at: "2026-09-10T10:00:00Z",
      updated_at: "2026-10-22T09:15:00Z"
    }
  },
  {
    id: "emp-2",
    name: "Marcus Vance",
    email: "marcus.vance@acme.com",
    role: "Senior Reliability & Backend Engineer",
    cost_per_hour: 95,
    weekly_capacity_hours: 40,
    max_overtime_hours: 10,
    start_date: "2024-03-01",
    career_goals: ["Mastering distributed streaming systems"],
    is_active: true,
    skills: [
      { id: "es-5", skill_id: "sk-3", skill_name: "Python", proficiency: 4, growth_target: 5 },
      { id: "es-6", skill_id: "sk-5", skill_name: "PostgreSQL", proficiency: 5, growth_target: 5 },
      { id: "es-7", skill_id: "sk-6", skill_name: "Docker", proficiency: 4, growth_target: 5 },
    ],
    leaves: [],
    dossier: {
      id: "dos-2",
      employee_id: "emp-2",
      employee_name: "Marcus Vance",
      employee_role: "Senior Reliability & Backend Engineer",
      employee_email: "marcus.vance@acme.com",
      archetype: "Firefighter",
      archetype_rationale: "Unmatched expertise in live production triage, critical incident resolution, and database lock recovery.",
      burnout_risk_score: 0.68,
      burnout_factors: [
        "Logged 45+ hours for 5 consecutive weeks on emergency stability sprint",
        "High on-call rotation frequency in recent 2 months"
      ],
      coaching_sentiment: "High Autonomy Individual Contributor",
      client_facing_comfort: "Moderate (Effective with technical client peers)",
      preferred_team_size: "Standard Agile squad (3-6 members)",
      strengths_summary: [
        "PostgreSQL query optimization and deadlock recovery",
        "Rapid production troubleshooting under high stress"
      ],
      growth_areas: ["Needs workload pacing to prevent burnout; avoid consecutive overtime"],
      career_aspirations: ["Strengthening observability architecture", "Automating disaster recovery runs"],
      stretch_readiness_score: 0.80,
      profile_summary: "Firefighter archetype with exceptional recovery reflexes, but showing 68% fatigue index due to crunch sprints. Advise rotating off on-call.",
      confidence_overall: 0.92,
      enrichment_level: 2,
      evidence_citations: [
        {
          skill: "PostgreSQL",
          proficiency: 5,
          confidence: 0.96,
          evidence: "Resolved critical connection starvation incident in under 12 minutes during Black Friday peak.",
          sources: ["performance_report", "activity_log"]
        },
        {
          skill: "Python",
          proficiency: 4,
          confidence: 0.88,
          evidence: "Maintains core database migration scripts and background worker tasks.",
          sources: ["resume", "activity_log"]
        }
      ],
      documents: [
        { id: "doc-4", filename: "marcus_vance_cv.pdf", file_type: "pdf", category: "resume", created_at: "2026-08-01T10:00:00Z" },
        { id: "doc-5", filename: "incident_response_activity_log.txt", file_type: "text", category: "activity_log", created_at: "2026-10-18T16:00:00Z" }
      ],
      created_at: "2026-08-01T10:00:00Z",
      updated_at: "2026-10-18T16:00:00Z"
    }
  },
  {
    id: "emp-3",
    name: "Elena Rostova",
    email: "elena.r@acme.com",
    role: "Frontend Tech Lead",
    cost_per_hour: 105,
    weekly_capacity_hours: 40,
    max_overtime_hours: 8,
    start_date: "2023-11-15",
    career_goals: ["Design system architecture", "Mentoring junior leads"],
    is_active: true,
    skills: [
      { id: "es-8", skill_id: "sk-1", skill_name: "React", proficiency: 5, growth_target: 5 },
      { id: "es-9", skill_id: "sk-2", skill_name: "TypeScript", proficiency: 5, growth_target: 5 },
      { id: "es-10", skill_id: "sk-10", skill_name: "UI/UX Design", proficiency: 4, growth_target: 5 },
    ],
    leaves: [],
    dossier: {
      id: "dos-3",
      employee_id: "emp-3",
      employee_name: "Elena Rostova",
      employee_role: "Frontend Tech Lead",
      employee_email: "elena.r@acme.com",
      archetype: "Optimizer",
      archetype_rationale: "Champions code hygiene, component reuse, design system tokens, and client bundle optimization.",
      burnout_risk_score: 0.18,
      burnout_factors: ["Balanced cadence with healthy sprint velocity"],
      coaching_sentiment: "Exemplary Coach & Mentor (High Multiplier)",
      client_facing_comfort: "High (Demonstrated UI prototypes to Fortune 500 leadership)",
      preferred_team_size: "Standard Agile squad (3-6 members)",
      strengths_summary: [
        "Accessible enterprise design system implementation",
        "React performance optimization and micro-frontends"
      ],
      growth_areas: ["Expanding server-side streaming and GraphQL federation"],
      career_aspirations: ["Staff Design Engineer", "Public tech talk speaker"],
      stretch_readiness_score: 0.90,
      profile_summary: "Optimizer archetype with 95% confidence rating across React and TypeScript. Praised as a standout team multiplier.",
      confidence_overall: 0.95,
      enrichment_level: 2,
      evidence_citations: [
        {
          skill: "React",
          proficiency: 5,
          confidence: 0.97,
          evidence: "Architected modern design system adopted by 8 product teams, reducing design churn by 60%.",
          sources: ["resume", "performance_report", "feedback_360"]
        },
        {
          skill: "TypeScript",
          proficiency: 5,
          confidence: 0.95,
          evidence: "Enforced strict type guards and zero-any rules across all core repositories.",
          sources: ["performance_report"]
        }
      ],
      documents: [
        { id: "doc-6", filename: "elena_rostova_resume.pdf", file_type: "pdf", category: "resume", created_at: "2026-07-20T11:00:00Z" },
        { id: "doc-7", filename: "q2_q3_performance_review.docx", file_type: "docx", category: "performance_report", created_at: "2026-10-10T12:00:00Z" }
      ],
      created_at: "2026-07-20T11:00:00Z",
      updated_at: "2026-10-10T12:00:00Z"
    }
  },
  {
    id: "emp-4",
    name: "Devon Brooks",
    email: "devon.b@acme.com",
    role: "Fullstack Engineer (Growth Focus)",
    cost_per_hour: 70,
    weekly_capacity_hours: 40,
    max_overtime_hours: 8,
    start_date: "2025-02-01",
    career_goals: ["Mastering Kubernetes & cloud DevOps", "Leading small feature pods"],
    is_active: true,
    skills: [
      { id: "es-11", skill_id: "sk-1", skill_name: "React", proficiency: 3, growth_target: 4 },
      { id: "es-12", skill_id: "sk-3", skill_name: "Python", proficiency: 3, growth_target: 4 },
      { id: "es-13", skill_id: "sk-7", skill_name: "Kubernetes", proficiency: 2, growth_target: 4 },
    ],
    leaves: [],
    dossier: {
      id: "dos-4",
      employee_id: "emp-4",
      employee_name: "Devon Brooks",
      employee_role: "Fullstack Engineer (Growth Focus)",
      employee_email: "devon.b@acme.com",
      archetype: "Mentor",
      archetype_rationale: "Shows great enthusiasm for learning, documentation, and paired programming sessions.",
      burnout_risk_score: 0.15,
      burnout_factors: ["Normal healthy workload"],
      coaching_sentiment: "Eager Learner & Collaborative Contributor",
      client_facing_comfort: "Moderate (Great at preparing demo slides)",
      preferred_team_size: "Focused strike team (2-4 members)",
      strengths_summary: ["Fast learner", "Highly responsive to feedback", "Diligent automated test writer"],
      growth_areas: ["Requires paired mentorship when touching Kubernetes production clusters"],
      career_aspirations: ["Promoting to Senior Fullstack Engineer", "Leading cloud migration projects"],
      stretch_readiness_score: 0.88,
      profile_summary: "High-potential growth profile. Ideal for stretch assignments under the guidance of Sarah Chen or Marcus Vance.",
      confidence_overall: 0.86,
      enrichment_level: 1,
      evidence_citations: [
        {
          skill: "Python",
          proficiency: 3,
          confidence: 0.85,
          evidence: "Implemented user authentication and webhook dispatchers with 90%+ pytest coverage.",
          sources: ["resume", "activity_log"]
        },
        {
          skill: "React",
          proficiency: 3,
          confidence: 0.84,
          evidence: "Built dashboard filters and interactive data table components.",
          sources: ["activity_log"]
        }
      ],
      documents: [
        { id: "doc-8", filename: "devon_brooks_cv.pdf", file_type: "pdf", category: "resume", created_at: "2026-09-01T09:00:00Z" }
      ],
      created_at: "2026-09-01T09:00:00Z",
      updated_at: "2026-09-01T09:00:00Z"
    }
  }
];

export const MOCK_PROJECTS: Project[] = [
  {
    id: "proj-1",
    name: "Fintech Real-Time Ledger",
    client_name: "Apex Global Capital",
    revenue: 420000,
    priority: 5,
    is_mandatory: true,
    start_date: "2026-11-01",
    end_date: "2027-01-31",
    roles: [
      {
        id: "role-1",
        role_name: "Lead Cloud Architect",
        hours_per_week: 40,
        start_week: 1,
        end_week: 12,
        allow_stretch: false,
        skills: [
          { id: "rps-1", skill_id: "sk-3", skill_name: "Python", required_proficiency: 4 },
          { id: "rps-2", skill_id: "sk-8", skill_name: "Distributed Systems", required_proficiency: 4 }
        ]
      },
      {
        id: "role-2",
        role_name: "Core Data & Backend Engineer",
        hours_per_week: 40,
        start_week: 1,
        end_week: 12,
        allow_stretch: true,
        skills: [
          { id: "rps-3", skill_id: "sk-5", skill_name: "PostgreSQL", required_proficiency: 4 },
          { id: "rps-4", skill_id: "sk-3", skill_name: "Python", required_proficiency: 3 }
        ]
      }
    ]
  },
  {
    id: "proj-2",
    name: "Healthcare Analytics Portal",
    client_name: "MediCare Systems",
    revenue: 285000,
    priority: 4,
    is_mandatory: false,
    start_date: "2026-11-01",
    end_date: "2027-01-31",
    roles: [
      {
        id: "role-3",
        role_name: "Frontend Lead",
        hours_per_week: 40,
        start_week: 1,
        end_week: 12,
        allow_stretch: false,
        skills: [
          { id: "rps-5", skill_id: "sk-1", skill_name: "React", required_proficiency: 4 },
          { id: "rps-6", skill_id: "sk-2", skill_name: "TypeScript", required_proficiency: 4 }
        ]
      }
    ]
  }
];

export const MOCK_PLAN: Plan = {
  id: "plan-mock-1",
  name: "Q4 High-Margin Strategic Staffing",
  status: "approved",
  horizon_weeks: 12,
  tradeoff_slider: 0.65,
  profit_score: 412500,
  growth_score: 148000,
  balance_penalty: 12300,
  objective_breakdown: {
    profit: 412500,
    growth_score: 148000,
    revenue: 705000,
    labor_cost: 268000,
    overtime_cost: 14500,
    stretch_bonus: 35000,
    balance_penalty: 12300
  },
  assignments: [
    {
      id: "as-1",
      employee_id: "emp-1",
      employee_name: "Sarah Chen",
      project_id: "proj-1",
      project_name: "Fintech Real-Time Ledger",
      role_id: "role-1",
      role_name: "Lead Cloud Architect",
      week_number: 1,
      allocated_hours: 40,
      is_stretch: false,
      hourly_cost: 125,
      reasons: {
        skill_match: "Perfect 5/5 mastery in Distributed Systems and Python with 96% confidence rating",
        margin_contribution: "Generates $35,000 weekly gross profit contribution",
        mentor_synergy: "Designated mentor for Devon Brooks on paired cloud modules"
      }
    },
    {
      id: "as-2",
      employee_id: "emp-4",
      employee_name: "Devon Brooks",
      project_id: "proj-1",
      project_name: "Fintech Real-Time Ledger",
      role_id: "role-2",
      role_name: "Core Data & Backend Engineer",
      week_number: 1,
      allocated_hours: 40,
      is_stretch: true,
      mentor_id: "emp-1",
      mentor_name: "Sarah Chen",
      hourly_cost: 70,
      reasons: {
        skill_match: "Level 3 Python meets threshold for stretch placement",
        growth_alignment: "Fulfills explicit 1-on-1 career goal of backend high-throughput mastery",
        mentor_synergy: "Paired with Sarah Chen (Principal Architect) with 10% capacity mentorship dedication"
      }
    },
    {
      id: "as-3",
      employee_id: "emp-3",
      employee_name: "Elena Rostova",
      project_id: "proj-2",
      project_name: "Healthcare Analytics Portal",
      role_id: "role-3",
      role_name: "Frontend Lead",
      week_number: 1,
      allocated_hours: 40,
      is_stretch: false,
      hourly_cost: 105,
      reasons: {
        skill_match: "5/5 React & TypeScript proficiency verified across multiple client deliveries",
        margin_contribution: "Preserves 54% project margin while leading healthcare accessibility standards"
      }
    }
  ]
};

export const MOCK_SCENARIOS: Scenario[] = [
  {
    id: "sc-1",
    name: "Fintech Project Fast-Track (Pull Date Forward 3 Weeks)",
    description: "Evaluates impact if Apex Global pulls project kickoff forward into mid-October.",
    baseline_plan_id: "plan-mock-1",
    scenario_plan_id: "plan-sc-1",
    diff_summary: {
      profit_diff: 45000,
      growth_diff: -12000,
      assignments_changed: 6,
      projects_added: 0,
      projects_dropped: 0
    },
    created_at: "2026-10-28T14:00:00Z"
  },
  {
    id: "sc-2",
    name: "Marcus Vance Workload Relief (Burnout Protection)",
    description: "Replaces overtime on emergency incident sprints with contractor backfill.",
    baseline_plan_id: "plan-mock-1",
    scenario_plan_id: "plan-sc-2",
    diff_summary: {
      profit_diff: -8500,
      growth_diff: 15000,
      assignments_changed: 4,
      projects_added: 0,
      projects_dropped: 0
    },
    created_at: "2026-10-29T11:20:00Z"
  }
];

export const MOCK_PARETO: ParetoPoint[] = [
  { slider_value: 0.0, profit: 450000, growth: 80000, label: "Max Profit (0.0)" },
  { slider_value: 0.25, profit: 438000, growth: 110000, label: "Profit Leaning (0.25)" },
  { slider_value: 0.5, profit: 425000, growth: 135000, label: "Balanced (0.50)" },
  { slider_value: 0.65, profit: 412500, growth: 148000, label: "Strategic Growth (0.65)" },
  { slider_value: 1.0, profit: 375000, growth: 185000, label: "Max Growth & Retention (1.0)" },
];

export const MOCK_ADVISORY: CognitiveAdvisory = {
  plan_id: "plan-mock-1",
  plan_name: "Q4 High-Margin Strategic Staffing",
  advisor_name: "Alex (AI Resource Manager)",
  executive_summary: "Here is my assessment of 'Q4 High-Margin Strategic Staffing': This allocation delivers a robust 58.5% gross margin ($412,500 net profit) across active squads. It strategically pairs 1 rising engineer (Devon Brooks) with certified principal architect Sarah Chen, while enforcing fatigue guardrails across high-utilization engineers (Marcus Vance) to curb turnover. Squad structure is anchored predominantly by 'Pathfinder' and 'Optimizer' profiles, ensuring high delivery cadence.",
  commercial_health: {
    net_profit: 412500,
    gross_revenue: 705000,
    gross_margin_pct: 58.5,
    labor_cost: 268000,
    overtime_cost: 14500,
    commercial_rating: "Exceptional",
  },
  people_and_chemistry: {
    active_staff_count: 4,
    mentorship_pairings: [
      {
        mentee_id: "emp-4",
        mentee_name: "Devon Brooks",
        mentor_id: "emp-1",
        mentor_name: "Sarah Chen",
        coaching_sentiment: "Exemplary Coach & Mentor (High Multiplier)",
        project_name: "Fintech Real-Time Ledger",
        role_title: "Core Data & Backend Engineer",
      },
    ],
    stretch_assignments: [
      {
        employee_name: "Devon Brooks",
        role_title: "Core Data & Backend Engineer",
        target_skills: ["Python", "Distributed Systems"],
        mentor_name: "Sarah Chen",
      },
    ],
    archetype_distribution: {
      Pathfinder: 1,
      Optimizer: 1,
      Firefighter: 1,
      Mentor: 1,
    },
    fatigue_mitigation_alerts: [
      {
        name: "Marcus Vance",
        fatigue_pct: 78,
        max_week_hours: 40,
        status: "Protected",
        recommendation: "Workload successfully throttled to 40h/w without overtime spikes to prevent emergency response churn.",
      },
    ],
  },
  strategic_recommendations: [
    {
      category: "Mentorship & Chemistry",
      severity: "Positive",
      title: "Paired Acceleration: Devon Brooks & Sarah Chen",
      detail: "Devon is stretching into high-throughput backend modules on Fintech Ledger. Sarah Chen has reserved 10% capacity for weekly PR reviews and architecture guidance.",
    },
    {
      category: "Burnout Protection",
      severity: "Warning",
      title: "Fatigue Watch: Marcus Vance (78% Stress)",
      detail: "Marcus's historical on-call paging requires strict 40h capping. Do not schedule emergency incident shifts during Week 3-4.",
    },
    {
      category: "Commercial Margin",
      severity: "Neutral",
      title: "Blended Rate Arbitrage: 58.5% Margin",
      detail: "Staffing Devon ($70/hr) with senior oversight rather than a second lead architect ($125/hr) saves $2,200/wk while hitting all deliverables.",
    },
  ],
};

