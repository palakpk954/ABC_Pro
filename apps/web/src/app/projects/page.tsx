"use client";

import React, { useState } from "react";
import { MOCK_PROJECTS } from "@/lib/mockData";
import { Project } from "@/lib/api";
import { CsvImportModal } from "@/components/data/CsvImportModal";
import { formatCurrency, cn } from "@/lib/utils";
import { 
  Plus, 
  Upload, 
  Building2, 
  Calendar, 
  Star, 
  Award, 
  CheckCircle2, 
} from "lucide-react";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>(MOCK_PROJECTS);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  // New project state
  const [newName, setNewName] = useState("");
  const [newClient, setNewClient] = useState("");
  const [newRevenue, setNewRevenue] = useState(250000);
  const [newPriority, setNewPriority] = useState(4);
  const [newMandatory, setNewMandatory] = useState(false);

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName || !newClient) return;

    const newProj: Project = {
      id: `proj-${Date.now()}`,
      name: newName,
      client: newClient,
      start_date: "2026-11-02",
      end_date: "2027-01-22",
      revenue: newRevenue,
      billing_rate_hourly: 175,
      priority: newPriority,
      mandatory: newMandatory,
      status: "proposed",
      roles: [
        {
          id: `role-${Date.now()}`,
          project_id: `proj-${Date.now()}`,
          role_title: "Senior Fullstack Lead",
          hours_per_week: 40,
          start_date: "2026-11-02",
          end_date: "2027-01-22",
          is_stretch_allowed: true,
          skill_requirements: [
            { id: `rs-1`, skill_id: "sk-1", skill_name: "React", min_proficiency: 4 },
            { id: `rs-2`, skill_id: "sk-4", skill_name: "Python", min_proficiency: 4 },
          ],
        },
      ],
    };

    setProjects([newProj, ...projects]);
    setShowAddModal(false);
    setNewName("");
    setNewClient("");
    setNotification(`Project "${newProj.name}" created and added to candidate portfolio.`);
    setTimeout(() => setNotification(null), 4000);
  };

  const handleImportSuccess = (count: number) => {
    setNotification(`Successfully imported ${count} projects and roles from CSV.`);
    setTimeout(() => setNotification(null), 4000);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="rounded-md bg-indigo-50 dark:bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
              Demand & Engagements
            </span>
            <span className="text-xs text-muted-foreground">{projects.length} Candidate Engagements</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Projects & Role Demands</h1>
          <p className="text-xs text-muted-foreground mt-1">
            Configure client contracts, project revenue, priority rankings, mandatory constraints, and required skills.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setIsImportModalOpen(true)}
            id="import-projects-btn"
            className="flex items-center gap-2 rounded-xl bg-white dark:bg-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors shadow-sm"
          >
            <Upload className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            Import CSV
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            id="add-project-btn"
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-indigo-600/20 hover:bg-indigo-500 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Add Engagement
          </button>
        </div>
      </div>

      {notification && (
        <div className="rounded-xl border border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-950/40 p-3.5 text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2.5 animate-accordion-down">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
          <span>{notification}</span>
        </div>
      )}

      {/* Projects List */}
      <div className="space-y-4">
        {projects.map((proj) => (
          <div
            key={proj.id}
            className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-6 backdrop-blur-xl transition-all hover:border-indigo-500/30 hover:shadow-md dark:hover:shadow-xl shadow-sm"
          >
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-3">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">{proj.name}</h3>
                  {proj.mandatory && (
                    <span className="rounded-md bg-rose-50 dark:bg-rose-500/15 px-2 py-0.5 text-xs font-bold text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-500/30">
                      Mandatory (HC-3)
                    </span>
                  )}
                  <span
                    className={cn(
                      "rounded-md px-2 py-0.5 text-xs font-semibold uppercase tracking-wider",
                      proj.status === "active"
                        ? "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/15 dark:text-emerald-300 dark:border-emerald-500/30"
                        : proj.status === "dropped"
                        ? "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-500/15 dark:text-rose-300 dark:border-rose-500/30"
                        : "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-500/15 dark:text-blue-300 dark:border-blue-500/30"
                    )}
                  >
                    {proj.status}
                  </span>
                </div>

                <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300 font-medium">
                    <Building2 className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" /> {proj.client}
                  </span>
                  <span className="flex items-center gap-1.5 text-amber-600 dark:text-amber-300 font-semibold">
                    <Star className="h-3.5 w-3.5 fill-amber-500 text-amber-500 dark:fill-amber-300 dark:text-amber-300" /> Priority {proj.priority} / 5
                  </span>
                  <span className="flex items-center gap-1.5 font-mono">
                    <Calendar className="h-3.5 w-3.5 text-slate-400" /> 12 Weeks (Nov 2 – Jan 22)
                  </span>
                </div>
              </div>

              <div className="text-left lg:text-right">
                <span className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
                  {formatCurrency(proj.revenue)}
                </span>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Est. Rate: ${proj.billing_rate_hourly || 175}/hr
                </p>
              </div>
            </div>

            {/* Roles Demand Breakdown */}
            <div className="mt-5 border-t border-slate-200 dark:border-white/5 pt-4">
              <div className="flex items-center justify-between mb-3 text-xs">
                <span className="font-semibold text-slate-800 dark:text-slate-300">
                  Required Staffing Roles ({proj.roles.length})
                </span>
                <span className="text-muted-foreground text-[11px]">
                  HC-2: All selected project roles must be 100% staffed weekly
                </span>
              </div>

              {proj.roles.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">No roles defined for this project.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {proj.roles.map((r) => (
                    <div
                      key={r.id}
                      className="rounded-xl border border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-slate-800/40 p-3.5 text-xs transition-colors hover:bg-slate-100 dark:hover:bg-slate-800/70"
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-semibold text-slate-900 dark:text-slate-200">{r.role_title}</span>
                        <span className="font-mono text-indigo-700 dark:text-indigo-300 font-bold">{r.hours_per_week}h/w</span>
                      </div>

                      <div className="flex items-center gap-2 mb-2 text-[11px]">
                        {r.is_stretch_allowed ? (
                          <span className="flex items-center gap-1 text-purple-700 dark:text-purple-300 font-medium">
                            <Award className="h-3.5 w-3.5 text-purple-600 dark:text-purple-400" /> Stretch Allowed (Requires Mentor)
                          </span>
                        ) : (
                          <span className="text-muted-foreground">Strict Proficiency Required</span>
                        )}
                      </div>

                      {/* Required Skills */}
                      <div className="flex flex-wrap gap-1.5 border-t border-slate-200 dark:border-white/5 pt-2">
                        {(r.skill_requirements || r.skills || []).map((sr: any) => (
                          <span
                            key={sr.id}
                            className="rounded bg-white dark:bg-slate-700/60 px-2 py-0.5 text-[11px] text-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-600/50 shadow-xs"
                          >
                            {sr.skill_name || "Skill"} &ge;{" "}
                            <strong className="text-slate-900 dark:text-white font-mono">Level {sr.min_proficiency}</strong>
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* CSV Import Modal */}
      <CsvImportModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        entityName="Projects & Roles"
        onSuccess={handleImportSuccess}
      />

      {/* Add Project Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-lg rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 p-6 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-foreground">
            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">Add Candidate Engagement</h3>
            <p className="text-xs text-muted-foreground mb-4">
              Register project scope, client revenue, and strategic priority.
            </p>

            <form onSubmit={handleCreateProject} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Project Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Cloud Security Modernization"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Client Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. FinTech Global"
                    value={newClient}
                    onChange={(e) => setNewClient(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Total Revenue ($)</label>
                  <input
                    type="number"
                    min="10000"
                    step="5000"
                    value={newRevenue}
                    onChange={(e) => setNewRevenue(parseInt(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Priority (1 to 5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={newPriority}
                    onChange={(e) => setNewPriority(parseInt(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 p-3 border border-slate-200 dark:border-white/5">
                <input
                  type="checkbox"
                  id="mandatory-checkbox"
                  checked={newMandatory}
                  onChange={(e) => setNewMandatory(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 h-4 w-4"
                />
                <label htmlFor="mandatory-checkbox" className="text-slate-700 dark:text-slate-300 font-medium cursor-pointer">
                  Mandatory Project (Must be selected by solver; reports conflicts if infeasible)
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-200 dark:border-white/10">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="rounded-xl px-4 py-2 text-muted-foreground hover:text-slate-900 dark:hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-indigo-600 px-4 py-2 font-semibold text-white shadow hover:bg-indigo-500"
                >
                  Save Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
