"use client";

import React, { useState } from "react";
import { MOCK_EMPLOYEES } from "@/lib/mockData";
import { Employee, MultiSourceUploadSummary } from "@/lib/api";
import { CsvImportModal } from "@/components/data/CsvImportModal";
import { MultiSourceImportModal } from "@/components/data/MultiSourceImportModal";
import { EmployeeDossierModal } from "@/components/dossier/EmployeeDossierModal";
import { formatCurrency, cn } from "@/lib/utils";
import { 
  Plus, 
  Upload, 
  Search, 
  Target, 
  CheckCircle2,
  Clock,
  Sparkles,
  Award,
  ShieldCheck,
  Flame,
  UserCheck,
  Filter
} from "lucide-react";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>(MOCK_EMPLOYEES);
  const [searchQuery, setSearchQuery] = useState("");
  const [archetypeFilter, setArchetypeFilter] = useState<string>("ALL");
  const [burnoutFilter, setBurnoutFilter] = useState<string>("ALL");
  
  // Modals state
  const [isCsvImportOpen, setIsCsvImportOpen] = useState(false);
  const [isMultiSourceModalOpen, setIsMultiSourceModalOpen] = useState(false);
  const [selectedEmpForUpload, setSelectedEmpForUpload] = useState<string | undefined>(undefined);
  const [selectedEmpForDossier, setSelectedEmpForDossier] = useState<Employee | null>(null);
  const [isDossierModalOpen, setIsDossierModalOpen] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  // New employee form state
  const [newName, setNewName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState("Fullstack Engineer");
  const [newCost, setNewCost] = useState(80);
  const [newCapacity, setNewCapacity] = useState(40);
  const [newGoals, setNewGoals] = useState("");

  const filteredEmployees = employees.filter((e) => {
    const matchesSearch =
      e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.role.toLowerCase().includes(searchQuery.toLowerCase());

    const arch = e.dossier?.archetype || "Generalist";
    const matchesArchetype = archetypeFilter === "ALL" || arch === archetypeFilter;

    const burnout = e.dossier?.burnout_risk_score || 0.15;
    const matchesBurnout =
      burnoutFilter === "ALL" ||
      (burnoutFilter === "HIGH" && burnout >= 0.5) ||
      (burnoutFilter === "MODERATE" && burnout >= 0.3 && burnout < 0.5) ||
      (burnoutFilter === "HEALTHY" && burnout < 0.3);

    return matchesSearch && matchesArchetype && matchesBurnout;
  });

  const handleCreateEmployee = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName || !newEmail) return;

    const newEmp: Employee = {
      id: `emp-${Date.now()}`,
      name: newName,
      email: newEmail,
      role: newRole,
      cost_per_hour: newCost,
      weekly_capacity_hours: newCapacity,
      max_overtime_hours: 8,
      start_date: "2026-11-01",
      career_goals: newGoals ? [newGoals] : ["Continuous skill growth"],
      is_active: true,
      skills: [
        { id: `es-${Date.now()}`, skill_id: "sk-1", skill_name: "React", proficiency: 4, growth_target: 5 },
      ],
      leaves: [],
      dossier: {
        id: `dos-${Date.now()}`,
        employee_id: `emp-${Date.now()}`,
        employee_name: newName,
        employee_role: newRole,
        employee_email: newEmail,
        archetype: "Generalist",
        archetype_rationale: "Newly added employee profile ready for document ingestion.",
        burnout_risk_score: 0.15,
        burnout_factors: ["Normal onboarding capacity"],
        coaching_sentiment: "Collaborative Contributor",
        client_facing_comfort: "Moderate",
        preferred_team_size: "3-6 members",
        strengths_summary: [`Initial baseline in ${newRole}`],
        growth_areas: ["Ready for multi-source ingestion"],
        career_aspirations: [newGoals || "Skill growth"],
        stretch_readiness_score: 0.70,
        profile_summary: `Initial profile for ${newName}. Ingest resumes or reviews to calibrate living dossier.`,
        confidence_overall: 0.70,
        enrichment_level: 0,
        evidence_citations: [],
        documents: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
    };

    setEmployees([newEmp, ...employees]);
    setShowAddModal(false);
    setNewName("");
    setNewEmail("");
    setNewGoals("");
    setNotification(`Employee "${newEmp.name}" added successfully.`);
    setTimeout(() => setNotification(null), 4000);
  };

  const handleOpenDossier = (emp: Employee) => {
    setSelectedEmpForDossier(emp);
    setIsDossierModalOpen(true);
  };

  const handleOpenUploadForEmp = (employeeId: string) => {
    setSelectedEmpForUpload(employeeId);
    setIsDossierModalOpen(false);
    setIsMultiSourceModalOpen(true);
  };

  const handleMultiSourceSuccess = (summary: MultiSourceUploadSummary) => {
    setEmployees((prev) =>
      prev.map((emp) => {
        if (emp.id === summary.employee_id) {
          const currentDossier = emp.dossier;
          return {
            ...emp,
            dossier: {
              ...currentDossier,
              id: currentDossier?.id || `dos-${emp.id}`,
              employee_id: emp.id,
              employee_name: emp.name,
              employee_role: emp.role,
              employee_email: emp.email,
              archetype: summary.archetype,
              archetype_rationale: `Enriched via ${summary.categories_detected.join(", ")} document analysis.`,
              burnout_risk_score: summary.burnout_risk_score,
              burnout_factors: currentDossier?.burnout_factors || ["Document analyzed"],
              coaching_sentiment: currentDossier?.coaching_sentiment || "Collaborative Contributor",
              client_facing_comfort: currentDossier?.client_facing_comfort || "Moderate",
              preferred_team_size: currentDossier?.preferred_team_size || "3-6 members",
              strengths_summary: currentDossier?.strengths_summary || ["Extracted core competency"],
              growth_areas: currentDossier?.growth_areas || ["Continuous development"],
              career_aspirations: currentDossier?.career_aspirations || emp.career_goals,
              stretch_readiness_score: summary.enrichment_level_reached >= 2 ? 0.90 : 0.80,
              profile_summary: summary.message,
              confidence_overall: summary.confidence_overall,
              enrichment_level: summary.enrichment_level_reached,
              evidence_citations: currentDossier?.evidence_citations || [],
              documents: currentDossier?.documents || [],
              created_at: currentDossier?.created_at || new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }
          };
        }
        return emp;
      })
    );

    setNotification(summary.message);
    setTimeout(() => setNotification(null), 5000);
  };

  const getArchetypeBadge = (archetype?: string) => {
    switch (archetype) {
      case "Pathfinder":
        return "bg-purple-500/10 text-purple-700 dark:text-purple-400 border-purple-500/20";
      case "Optimizer":
        return "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20";
      case "Firefighter":
        return "bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/20";
      case "Mentor":
        return "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/20";
      default:
        return "bg-slate-500/10 text-slate-700 dark:text-slate-400 border-slate-500/20";
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="rounded-md bg-indigo-50 dark:bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
              Living Talent Pool & Cognitive Profiles
            </span>
            <span className="text-xs text-muted-foreground">{employees.length} Engineers</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Employee Roster & Living Dossiers
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Dynamic talent profiles synthesized from Resumes, Reviews, 360 Feedback, and Delivery Cadence logs.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => {
              setSelectedEmpForUpload(undefined);
              setIsMultiSourceModalOpen(true);
            }}
            id="multi-source-ingest-btn"
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-indigo-600/20 hover:from-indigo-500 hover:to-purple-500 transition-all"
          >
            <Sparkles className="h-4 w-4" />
            Ingest Multi-Source Data
          </button>
          <button
            onClick={() => setIsCsvImportOpen(true)}
            id="import-employees-btn"
            className="flex items-center gap-2 rounded-xl bg-white dark:bg-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors shadow-sm"
          >
            <Upload className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            Import CSV
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            id="add-employee-btn"
            className="flex items-center gap-2 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-3.5 py-2 text-xs font-semibold shadow-sm hover:opacity-90 transition-all"
          >
            <Plus className="h-4 w-4" />
            Add Engineer
          </button>
        </div>
      </div>

      {notification && (
        <div className="rounded-xl border border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-950/40 p-3.5 text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2.5 animate-accordion-down">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
          <span>{notification}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by name, role, skill, or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/80 pl-10 pr-4 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/80 px-2.5 py-1.5 text-xs shadow-sm">
            <span className="text-[11px] font-semibold text-muted-foreground">Archetype:</span>
            <select
              value={archetypeFilter}
              onChange={(e) => setArchetypeFilter(e.target.value)}
              className="bg-transparent text-xs font-medium text-slate-900 dark:text-white focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Archetypes</option>
              <option value="Pathfinder">Pathfinder</option>
              <option value="Optimizer">Optimizer</option>
              <option value="Firefighter">Firefighter</option>
              <option value="Mentor">Mentor</option>
              <option value="Generalist">Generalist</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/80 px-2.5 py-1.5 text-xs shadow-sm">
            <span className="text-[11px] font-semibold text-muted-foreground">Fatigue:</span>
            <select
              value={burnoutFilter}
              onChange={(e) => setBurnoutFilter(e.target.value)}
              className="bg-transparent text-xs font-medium text-slate-900 dark:text-white focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Levels</option>
              <option value="HIGH">High Stress (&gt;50%)</option>
              <option value="MODERATE">Moderate (30-50%)</option>
              <option value="HEALTHY">Sustainable (&lt;30%)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Employees Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredEmployees.map((emp) => {
          const dos = emp.dossier;
          const archetype = dos?.archetype || "Generalist";
          const confidence = dos?.confidence_overall || 0.70;
          const burnout = dos?.burnout_risk_score || 0.15;

          return (
            <div
              key={emp.id}
              className="relative flex flex-col justify-between rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl transition-all hover:border-indigo-500/40 hover:shadow-lg dark:hover:shadow-2xl shadow-sm"
            >
              <div>
                {/* Header: Name, Avatar, Rate & Archetype */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white font-bold ring-2 ring-white/10 shadow-md">
                      {emp.name.split(" ").map((n) => n[0]).join("")}
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                          {emp.name}
                        </h3>
                      </div>
                      <p className="text-xs text-muted-foreground">{emp.role}</p>
                    </div>
                  </div>

                  <span className="rounded-lg bg-emerald-50 dark:bg-emerald-500/10 px-2 py-1 text-[11px] font-mono font-bold text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20">
                    {formatCurrency(emp.cost_per_hour)}/h
                  </span>
                </div>

                {/* Cognitive Badges Row */}
                <div className="mt-3.5 flex flex-wrap items-center gap-1.5">
                  <span className={cn(
                    "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold",
                    getArchetypeBadge(archetype)
                  )}>
                    <Award className="h-3 w-3" />
                    {archetype}
                  </span>

                  <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-600 dark:text-emerald-400">
                    <ShieldCheck className="h-3 w-3" />
                    {Math.round(confidence * 100)}% Conf.
                  </span>

                  {burnout >= 0.5 && (
                    <span className="inline-flex items-center gap-1 rounded-full border border-rose-500/20 bg-rose-500/10 px-2 py-0.5 text-[10px] font-bold text-rose-600 dark:text-rose-400 animate-pulse">
                      <Flame className="h-3 w-3" />
                      {Math.round(burnout * 100)}% Stress
                    </span>
                  )}
                </div>

                {/* Capacity & Overtime specs */}
                <div className="mt-3 flex items-center justify-between rounded-xl bg-slate-50 dark:bg-slate-800/40 p-2.5 border border-slate-200 dark:border-white/5 text-xs text-slate-700 dark:text-slate-300 font-mono">
                  <span className="flex items-center gap-1.5 text-muted-foreground">
                    <Clock className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                    Cap: {emp.weekly_capacity_hours}h/w
                  </span>
                  <span>Max OT: +{emp.max_overtime_hours}h</span>
                </div>

                {/* Career Growth Goal */}
                {emp.career_goals.length > 0 && (
                  <div className="mt-2.5 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/20 p-2.5 border border-indigo-200 dark:border-indigo-500/20 text-xs">
                    <div className="flex items-center gap-1.5 text-indigo-700 dark:text-indigo-300 font-semibold mb-0.5">
                      <Target className="h-3.5 w-3.5" /> Growth Target
                    </div>
                    <p className="text-[11px] text-slate-700 dark:text-slate-300 italic leading-snug">
                      &ldquo;{emp.career_goals[0]}&rdquo;
                    </p>
                  </div>
                )}

                {/* Skills Preview */}
                <div className="mt-3 border-t border-slate-200 dark:border-white/5 pt-2.5">
                  <div className="flex items-center justify-between mb-1.5 text-xs">
                    <span className="text-muted-foreground text-[11px]">Core Skills</span>
                    <span className="text-[10px] text-slate-500">Proficiency</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {emp.skills.slice(0, 4).map((s) => (
                      <span
                        key={s.id}
                        className="flex items-center gap-1 rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-[11px] text-slate-800 dark:text-slate-300 border border-slate-200 dark:border-white/5"
                      >
                        <span>{s.skill_name}</span>
                        <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                          P{s.proficiency}
                        </span>
                      </span>
                    ))}
                    {emp.skills.length > 4 && (
                      <span className="text-[10px] text-muted-foreground self-center">
                        +{emp.skills.length - 4} more
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Button: View Living Dossier */}
              <div className="mt-4 pt-3 border-t border-slate-200 dark:border-white/5 flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleOpenDossier(emp)}
                  className="w-full flex items-center justify-center gap-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-500/20 py-2 text-xs font-bold text-indigo-700 dark:text-indigo-300 hover:bg-indigo-600 hover:text-white dark:hover:bg-indigo-600 transition-all shadow-sm"
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>360 Living Dossier</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Living Talent Dossier 360 Inspection Modal */}
      <EmployeeDossierModal
        isOpen={isDossierModalOpen}
        onClose={() => setIsDossierModalOpen(false)}
        employee={selectedEmpForDossier}
        onUploadMore={handleOpenUploadForEmp}
      />

      {/* Multi-Source Ingestion Modal */}
      <MultiSourceImportModal
        isOpen={isMultiSourceModalOpen}
        onClose={() => setIsMultiSourceModalOpen(false)}
        employees={employees}
        selectedEmployeeId={selectedEmpForUpload}
        onSuccess={handleMultiSourceSuccess}
      />

      {/* CSV Import Modal */}
      <CsvImportModal
        isOpen={isCsvImportOpen}
        onClose={() => setIsCsvImportOpen(false)}
        entityName="Employees & Skills"
        onSuccess={(count) => {
          setNotification(`Successfully imported ${count} employees from CSV with verified schema.`);
          setTimeout(() => setNotification(null), 4000);
        }}
      />

      {/* Add Employee Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-lg rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 p-6 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-foreground">
            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">Add New Engineer</h3>
            <p className="text-xs text-muted-foreground mb-4">
              Register employee capacity, cost basis, and initial strategic career growth goals.
            </p>

            <form onSubmit={handleCreateEmployee} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="e.g. Maya Lin"
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 p-2.5 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Work Email</label>
                  <input
                    type="email"
                    required
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    placeholder="maya.l@acme.com"
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 p-2.5 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Standard Role</label>
                <input
                  type="text"
                  required
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 p-2.5 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Hourly Cost ($/h)</label>
                  <input
                    type="number"
                    min="20"
                    max="500"
                    value={newCost}
                    onChange={(e) => setNewCost(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 p-2.5 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Weekly Hours</label>
                  <input
                    type="number"
                    min="10"
                    max="60"
                    value={newCapacity}
                    onChange={(e) => setNewCapacity(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 p-2.5 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Strategic Growth Goal</label>
                <input
                  type="text"
                  value={newGoals}
                  onChange={(e) => setNewGoals(e.target.value)}
                  placeholder="e.g. Transition to Kubernetes cluster orchestration"
                  className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 p-2.5 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-200 dark:border-white/10">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="rounded-xl px-4 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md hover:bg-indigo-500"
                >
                  Create Engineer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
