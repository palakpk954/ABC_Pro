"use client";

import React, { useState } from "react";
import { Plan, Assignment, Employee, Project } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Lock, Award, HeartHandshake, Users, Briefcase, Compass, Zap } from "lucide-react";

interface TimelineGanttProps {
  plan: Plan;
  employees: Employee[];
  projects: Project[];
  onSelectAssignment: (assignment: Assignment) => void;
}

export function TimelineGantt({
  plan,
  employees,
  projects,
  onSelectAssignment,
}: TimelineGanttProps) {
  const [viewMode, setViewMode] = useState<"employee" | "project">("employee");
  const horizonWeeks = plan.horizon_weeks || 12;

  // Assignments indexed by employee: empId -> week -> Assignment[]
  const employeeMap: Record<string, Record<number, Assignment[]>> = {};
  employees.forEach((emp) => {
    employeeMap[emp.id] = {};
    for (let w = 1; w <= horizonWeeks; w++) {
      employeeMap[emp.id][w] = [];
    }
  });

  // Assignments indexed by project: projId -> week -> Assignment[]
  const projectMap: Record<string, Record<number, Assignment[]>> = {};
  projects.forEach((proj) => {
    projectMap[proj.id] = {};
    for (let w = 1; w <= horizonWeeks; w++) {
      projectMap[proj.id][w] = [];
    }
  });

  plan.assignments.forEach((asgn) => {
    if (employeeMap[asgn.employee_id] && employeeMap[asgn.employee_id][asgn.week_number]) {
      employeeMap[asgn.employee_id][asgn.week_number].push(asgn);
    }
    if (asgn.project_id && projectMap[asgn.project_id] && projectMap[asgn.project_id][asgn.week_number]) {
      projectMap[asgn.project_id][asgn.week_number].push(asgn);
    }
  });

  return (
    <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl transition-all">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-5">
        <div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-white">Interactive Staffing Timeline</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Click any assignment block to view solver explainability, lock constraints, and mentor pairing.
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex items-center rounded-xl bg-slate-100 dark:bg-slate-800/80 p-1 border border-slate-200 dark:border-white/10 text-xs">
          <button
            onClick={() => setViewMode("employee")}
            id="view-mode-employee"
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-medium transition-all",
              viewMode === "employee"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-600 dark:text-muted-foreground hover:text-slate-900 dark:hover:text-white"
            )}
          >
            <Users className="h-3.5 w-3.5" />
            By Engineer
          </button>
          <button
            onClick={() => setViewMode("project")}
            id="view-mode-project"
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-medium transition-all",
              viewMode === "project"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-600 dark:text-muted-foreground hover:text-slate-900 dark:hover:text-white"
            )}
          >
            <Briefcase className="h-3.5 w-3.5" />
            By Project
          </button>
        </div>
      </div>

      {/* Grid Timeline Table */}
      <div className="overflow-x-auto pb-2">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-200 dark:border-white/5 text-[11px] text-slate-600 dark:text-muted-foreground font-mono">
              <th className="py-2.5 px-3 min-w-[220px] font-medium">
                {viewMode === "employee" ? "Engineer & Chemistry" : "Project & Client"}
              </th>
              {Array.from({ length: horizonWeeks }, (_, i) => (
                <th key={i + 1} className="py-2.5 px-1.5 text-center min-w-[70px] font-medium">
                  Week {i + 1}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-white/5">
            {viewMode === "employee"
              ? employees.map((emp) => {
                  const weeks = employeeMap[emp.id] || {};
                  const dossier = emp.dossier;
                  const burnoutScore = dossier?.burnout_risk_score ?? 0.15;
                  const isHighBurnout = burnoutScore >= 0.50;

                  return (
                    <tr key={emp.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/20 transition-colors">
                      <td className="py-3 px-3 align-middle">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="font-semibold text-slate-900 dark:text-slate-200">{emp.name}</span>
                          {dossier?.archetype && (
                            <span className="rounded bg-indigo-50 dark:bg-indigo-950/50 px-1.5 py-0.2 text-[9px] font-medium text-indigo-700 dark:text-indigo-300 border border-indigo-200/60 dark:border-indigo-500/20">
                              {dossier.archetype}
                            </span>
                          )}
                          {isHighBurnout && (
                            <span
                              className="rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-400 px-1.5 py-0.2 text-[9px] font-bold flex items-center gap-0.5"
                              title={`Burnout Watch: ${Math.round(burnoutScore * 100)}% stress`}
                            >
                              <Zap className="h-2.5 w-2.5 text-amber-500" />
                              {Math.round(burnoutScore * 100)}%
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-muted-foreground truncate max-w-[210px] mt-0.5">
                          {emp.role} &bull; ${emp.cost_per_hour}/h
                        </div>
                      </td>
                      {Array.from({ length: horizonWeeks }, (_, i) => {
                        const weekNum = i + 1;
                        const cellAssignments = weeks[weekNum] || [];

                        return (
                          <td key={weekNum} className="p-1 align-middle">
                            {cellAssignments.length === 0 ? (
                              <div className="h-10 rounded-lg border border-dashed border-slate-200 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-900/30 flex items-center justify-center text-[10px] text-slate-400 dark:text-slate-600">
                                —
                              </div>
                            ) : (
                              <div className="space-y-1">
                                {cellAssignments.map((asgn) => {
                                  const reasons: any = asgn.reasons;
                                  const hasArchetypeFit = Boolean(reasons?.archetype_fit);

                                  return (
                                    <button
                                      key={asgn.id}
                                      onClick={() => onSelectAssignment(asgn)}
                                      className={cn(
                                        "w-full rounded-lg p-1.5 text-left transition-all hover:scale-[1.02] border shadow-sm",
                                        asgn.is_stretch
                                          ? "bg-purple-50 text-purple-900 border-purple-200 dark:bg-purple-950/40 dark:border-purple-500/40 dark:text-purple-200"
                                          : "bg-indigo-50 text-indigo-900 border-indigo-200 dark:bg-indigo-950/40 dark:border-indigo-500/30 dark:text-indigo-200"
                                      )}
                                    >
                                      <div className="flex items-center justify-between text-[10px]">
                                        <span className="font-bold truncate max-w-[45px]">
                                          {asgn.allocated_hours || asgn.hours || 40}h
                                        </span>
                                        <div className="flex items-center gap-1">
                                          {asgn.is_locked && (
                                            <Lock className="h-2.5 w-2.5 text-amber-500 dark:text-amber-400" />
                                          )}
                                          {hasArchetypeFit && (
                                            <Compass className="h-2.5 w-2.5 text-blue-600 dark:text-blue-400" />
                                          )}
                                          {asgn.is_stretch && (
                                            <Award className="h-2.5 w-2.5 text-purple-600 dark:text-purple-400" />
                                          )}
                                          {asgn.mentor_name && (
                                            <HeartHandshake className="h-2.5 w-2.5 text-emerald-600 dark:text-emerald-400" />
                                          )}
                                        </div>
                                      </div>
                                      <p className="text-[9px] font-medium text-slate-700 dark:text-slate-300 truncate mt-0.5">
                                        {asgn.project_name?.split(" ")[0]}
                                      </p>
                                    </button>
                                  );
                                })}
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })
              : projects.map((proj) => {
                  const weeks = projectMap[proj.id] || {};
                  return (
                    <tr key={proj.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/20 transition-colors">
                      <td className="py-3 px-3 align-middle">
                        <div className="font-semibold text-slate-900 dark:text-slate-200">{proj.name}</div>
                        <div className="text-[10px] text-muted-foreground">
                          {proj.client || proj.client_name} &bull; Priority {proj.priority}
                        </div>
                      </td>
                      {Array.from({ length: horizonWeeks }, (_, i) => {
                        const weekNum = i + 1;
                        const cellAssignments = weeks[weekNum] || [];

                        return (
                          <td key={weekNum} className="p-1 align-middle">
                            {cellAssignments.length === 0 ? (
                              <div className="h-10 rounded-lg border border-dashed border-slate-200 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-900/30 flex items-center justify-center text-[10px] text-slate-400 dark:text-slate-600">
                                —
                              </div>
                            ) : (
                              <div className="space-y-1">
                                {cellAssignments.map((asgn) => (
                                  <button
                                    key={asgn.id}
                                    onClick={() => onSelectAssignment(asgn)}
                                    className="w-full rounded-lg p-1.5 text-left border bg-slate-50 border-slate-200 text-slate-800 hover:border-indigo-400 dark:bg-slate-800/60 dark:border-white/10 dark:text-slate-200 dark:hover:border-indigo-400/50 transition-all shadow-sm"
                                  >
                                    <div className="flex items-center justify-between text-[10px]">
                                      <span className="font-semibold truncate max-w-[45px]">
                                        {asgn.employee_name?.split(" ")[0]}
                                      </span>
                                      <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                                        {asgn.allocated_hours || asgn.hours || 40}h
                                      </span>
                                    </div>
                                    <p className="text-[9px] text-muted-foreground truncate">
                                      {asgn.role_title || asgn.role_name}
                                    </p>
                                  </button>
                                ))}
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
