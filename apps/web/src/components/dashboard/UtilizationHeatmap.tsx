"use client";

import React, { useState } from "react";
import { Employee, Assignment } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Award, HeartHandshake, Info } from "lucide-react";

interface UtilizationHeatmapProps {
  employees: Employee[];
  assignments: Assignment[];
  horizonWeeks: number;
}

export function UtilizationHeatmap({
  employees,
  assignments,
  horizonWeeks = 12,
}: UtilizationHeatmapProps) {
  const [selectedCell, setSelectedCell] = useState<{
    employee: Employee;
    week: number;
    hours: number;
    assignments: Assignment[];
  } | null>(null);

  // Compute weekly hours map: [empId][week] -> { hours, assignments }
  const matrix: Record<string, Record<number, { hours: number; assignments: Assignment[] }>> = {};
  employees.forEach((emp) => {
    matrix[emp.id] = {};
    for (let w = 1; w <= horizonWeeks; w++) {
      matrix[emp.id][w] = { hours: 0, assignments: [] };
    }
  });

  assignments.forEach((asgn) => {
    if (matrix[asgn.employee_id] && matrix[asgn.employee_id][asgn.week_number]) {
      matrix[asgn.employee_id][asgn.week_number].hours += (asgn.hours || asgn.allocated_hours || 0);
      matrix[asgn.employee_id][asgn.week_number].assignments.push(asgn);
    }
  });

  function getCellColor(hours: number, capacity: number) {
    if (hours === 0) {
      return "bg-slate-100/70 border-slate-200 text-slate-400 dark:bg-slate-900/60 dark:border-slate-800 dark:text-slate-500";
    }
    const ratio = hours / capacity;
    if (ratio < 0.6) {
      return "bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-950/40 dark:border-blue-900/40 dark:text-blue-300";
    }
    if (ratio <= 1.0) {
      return "bg-emerald-50 border-emerald-300 text-emerald-800 font-semibold dark:bg-emerald-950/50 dark:border-emerald-800/50 dark:text-emerald-300";
    }
    return "bg-amber-50 border-amber-300 text-amber-900 font-bold ring-1 ring-amber-400/40 dark:bg-amber-950/70 dark:border-amber-600/60 dark:text-amber-200 dark:ring-amber-500/30";
  }

  return (
    <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl transition-all">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">Team Utilization Heatmap</h3>
            <span className="rounded-md bg-indigo-50 dark:bg-indigo-500/10 px-2 py-0.5 text-xs font-medium text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
              {employees.length} Engineers &bull; {horizonWeeks} Weeks
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Weekly staffing hours vs standard capacity (40h). Gray = bench, Green = optimal, Amber = overtime.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <div className="h-3 w-3 rounded bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700" />
            <span>0h (Bench)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-3 w-3 rounded bg-blue-50 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-800/50" />
            <span>&lt;40h</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-3 w-3 rounded bg-emerald-50 dark:bg-emerald-950 border border-emerald-300 dark:border-emerald-700" />
            <span>40h (100%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-3 w-3 rounded bg-amber-50 dark:bg-amber-950 border border-amber-300 dark:border-amber-600" />
            <span>&gt;40h (Overtime)</span>
          </div>
        </div>
      </div>

      {/* Grid container */}
      <div className="overflow-x-auto pb-2">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-200 dark:border-white/5 text-[11px] text-muted-foreground font-mono">
              <th className="py-2.5 px-3 min-w-[180px] font-medium text-slate-700 dark:text-muted-foreground">Engineer & Role</th>
              {Array.from({ length: horizonWeeks }, (_, i) => (
                <th key={i + 1} className="py-2.5 px-1.5 text-center min-w-[42px] font-medium text-slate-700 dark:text-muted-foreground">
                  W{i + 1}
                </th>
              ))}
              <th className="py-2.5 px-3 text-right font-medium text-slate-700 dark:text-muted-foreground">Avg Util</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-white/5">
            {employees.map((emp) => {
              const empWeeks = matrix[emp.id] || {};
              let totalHours = 0;
              for (let w = 1; w <= horizonWeeks; w++) {
                totalHours += empWeeks[w]?.hours || 0;
              }
              const avgUtil = Math.round((totalHours / (horizonWeeks * emp.weekly_capacity_hours)) * 100);

              return (
                <tr key={emp.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5 px-3">
                    <div className="font-semibold text-slate-900 dark:text-slate-200">{emp.name}</div>
                    <div className="text-[10px] text-muted-foreground truncate max-w-[170px]">{emp.role}</div>
                  </td>

                  {Array.from({ length: horizonWeeks }, (_, i) => {
                    const weekNum = i + 1;
                    const cellData = empWeeks[weekNum] || { hours: 0, assignments: [] };
                    const hasStretch = cellData.assignments.some((a) => a.is_stretch);

                    return (
                      <td key={weekNum} className="p-1 text-center">
                        <button
                          onClick={() =>
                            setSelectedCell({
                              employee: emp,
                              week: weekNum,
                              hours: cellData.hours,
                              assignments: cellData.assignments,
                            })
                          }
                          className={cn(
                            "relative w-full h-8 rounded-md flex items-center justify-center text-[11px] transition-all hover:scale-105 hover:ring-2 hover:ring-indigo-400/50 border",
                            getCellColor(cellData.hours, emp.weekly_capacity_hours)
                          )}
                          title={`${emp.name} - Week ${weekNum}: ${cellData.hours}h`}
                        >
                          {cellData.hours > 0 ? `${cellData.hours}h` : "—"}
                          {hasStretch && (
                            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5 items-center justify-center rounded-full bg-purple-500 ring-1 ring-background" />
                          )}
                        </button>
                      </td>
                    );
                  })}

                  <td className="py-2.5 px-3 text-right font-mono font-semibold">
                    <span
                      className={cn(
                        "rounded px-1.5 py-0.5 text-[11px]",
                        avgUtil > 100
                          ? "bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300"
                          : avgUtil >= 85
                          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300"
                          : avgUtil >= 50
                          ? "bg-blue-100 text-blue-800 dark:bg-blue-500/20 dark:text-blue-300"
                          : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400"
                      )}
                    >
                      {avgUtil}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Selected Cell Modal/Drawer */}
      {selectedCell && (
        <div className="mt-4 rounded-xl border border-indigo-200 dark:border-indigo-500/30 bg-slate-50 dark:bg-slate-900/95 p-4 shadow-lg animate-accordion-down">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Info className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                {selectedCell.employee.name} &bull; Week {selectedCell.week} Detail
              </h4>
            </div>
            <button
              onClick={() => setSelectedCell(null)}
              className="text-xs text-muted-foreground hover:text-slate-900 dark:hover:text-white"
            >
              Close
            </button>
          </div>

          <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="rounded-lg bg-white dark:bg-slate-800/60 p-2.5 border border-slate-200 dark:border-white/5">
              <span className="text-muted-foreground">Allocated Hours</span>
              <p className="text-base font-bold text-slate-900 dark:text-white mt-0.5">
                {selectedCell.hours} / {selectedCell.employee.weekly_capacity_hours} hrs
                {selectedCell.hours > selectedCell.employee.weekly_capacity_hours && (
                  <span className="text-amber-600 dark:text-amber-400 text-xs ml-2">
                    (+{selectedCell.hours - selectedCell.employee.weekly_capacity_hours}h Overtime)
                  </span>
                )}
              </p>
            </div>
            <div className="rounded-lg bg-white dark:bg-slate-800/60 p-2.5 border border-slate-200 dark:border-white/5">
              <span className="text-muted-foreground">Active Engagements</span>
              <p className="text-base font-bold text-slate-900 dark:text-white mt-0.5">
                {selectedCell.assignments.length} Project Assignment(s)
              </p>
            </div>
            <div className="rounded-lg bg-white dark:bg-slate-800/60 p-2.5 border border-slate-200 dark:border-white/5">
              <span className="text-muted-foreground">Hourly Billing & Cost</span>
              <p className="text-base font-bold text-slate-900 dark:text-white mt-0.5">
                ${selectedCell.employee.cost_per_hour}/hr cost
              </p>
            </div>
          </div>

          {selectedCell.assignments.length > 0 && (
            <div className="mt-3 space-y-2">
              {selectedCell.assignments.map((asgn) => (
                <div
                  key={asgn.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-white dark:bg-slate-800/40 p-2.5 border border-slate-200 dark:border-white/5"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900 dark:text-slate-200">{asgn.project_name}</span>
                      <span className="text-slate-400 dark:text-slate-500">&bull;</span>
                      <span className="text-slate-600 dark:text-slate-400">{asgn.role_title}</span>
                      {asgn.is_stretch && (
                        <span className="flex items-center gap-1 rounded bg-purple-50 dark:bg-purple-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-500/30">
                          <Award className="h-3 w-3" /> Stretch Opportunity
                        </span>
                      )}
                      {asgn.mentor_name && (
                        <span className="flex items-center gap-1 rounded bg-emerald-50 dark:bg-emerald-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-500/30">
                          <HeartHandshake className="h-3 w-3" /> Mentor: {asgn.mentor_name}
                        </span>
                      )}
                    </div>
                    {asgn.reasons?.growth?.matched_goals && (
                      <p className="text-[11px] text-indigo-700 dark:text-indigo-300/90 mt-1">
                        🎯 Matched Goal: {asgn.reasons.growth.matched_goals.join(", ")}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-slate-900 dark:text-white">{asgn.hours}h</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
