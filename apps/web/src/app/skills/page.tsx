"use client";

import React, { useState } from "react";
import { MOCK_SKILLS, MOCK_EMPLOYEES } from "@/lib/mockData";
import { Employee, Skill, EmployeeSkill } from "@/lib/api";
import { cn } from "@/lib/utils";
import { 
  CheckCircle2, 
  Star
} from "lucide-react";

export default function SkillsMatrixPage() {
  const [skills, setSkills] = useState<Skill[]>(MOCK_SKILLS);
  const [employees, setEmployees] = useState<Employee[]>(MOCK_EMPLOYEES);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [editingCell, setEditingCell] = useState<{
    employeeId: string;
    skillId: string;
    employeeName: string;
    skillName: string;
    currentProficiency: number;
    currentTarget: number | null;
  } | null>(null);
  const [notification, setNotification] = useState<string | null>(null);

  const categories = ["All", "Frontend", "Backend", "Cloud/DevOps", "Architecture/AI"];

  const filteredSkills =
    selectedCategory === "All"
      ? skills
      : skills.filter((s) => s.category === selectedCategory);

  const handleSaveCell = (newProficiency: number, newTarget: number | null) => {
    if (!editingCell) return;

    setEmployees((prev) =>
      prev.map((emp) => {
        if (emp.id !== editingCell.employeeId) return emp;
        const exists = emp.skills.some((s) => s.skill_id === editingCell.skillId);
        const updatedSkills = exists
          ? emp.skills.map((s) =>
              s.skill_id === editingCell.skillId
                ? { ...s, proficiency: newProficiency, growth_target: newTarget }
                : s
            )
          : [
              ...emp.skills,
              {
                id: `es-${Date.now()}`,
                skill_id: editingCell.skillId,
                skill_name: editingCell.skillName,
                proficiency: newProficiency,
                growth_target: newTarget,
              },
            ];
        return { ...emp, skills: updatedSkills };
      })
    );

    setEditingCell(null);
    setNotification(
      `Updated ${editingCell.employeeName} on ${editingCell.skillName}: Proficiency Level ${newProficiency}`
    );
    setTimeout(() => setNotification(null), 4000);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="rounded-md bg-purple-50 dark:bg-purple-500/10 px-2 py-0.5 text-xs font-semibold text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-500/20">
              Competency & Development Matrix
            </span>
            <span className="text-xs text-muted-foreground">FR-23 Skills Grid</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Skills Matrix</h1>
          <p className="text-xs text-muted-foreground mt-1">
            Inspect and update organizational skill proficiencies (1-5) and aspirational growth targets (1-5).
          </p>
        </div>

        {/* Category Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto rounded-xl bg-slate-100 dark:bg-slate-800/80 p-1 border border-slate-200 dark:border-white/10 text-xs">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={cn(
                "rounded-lg px-3 py-1.5 font-medium transition-all whitespace-nowrap",
                selectedCategory === cat
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-600 dark:text-muted-foreground hover:text-slate-900 dark:hover:text-white"
              )}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {notification && (
        <div className="rounded-xl border border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-950/40 p-3.5 text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2.5 animate-accordion-down">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
          <span>{notification}</span>
        </div>
      )}

      {/* Skills Matrix Table */}
      <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl overflow-x-auto transition-all">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-200 dark:border-white/10 text-[11px] text-muted-foreground font-mono">
              <th className="py-3 px-4 min-w-[200px] font-semibold text-slate-900 dark:text-white">
                Engineer
              </th>
              {filteredSkills.map((sk) => (
                <th key={sk.id} className="py-3 px-2 text-center min-w-[100px] font-semibold text-slate-800 dark:text-slate-300">
                  <div>{sk.name}</div>
                  <div className="text-[9px] font-normal text-muted-foreground font-sans">{sk.category}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-white/5">
            {employees.map((emp) => {
              const skillMap: Record<string, EmployeeSkill> = {};
              emp.skills.forEach((s) => {
                skillMap[s.skill_id] = s;
              });

              return (
                <tr key={emp.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/20 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900 dark:text-white">{emp.name}</div>
                    <div className="text-[10px] text-muted-foreground">{emp.role}</div>
                  </td>

                  {filteredSkills.map((sk) => {
                    const empSkill = skillMap[sk.id];
                    const prof = empSkill?.proficiency || 0;
                    const target = empSkill?.growth_target;

                    return (
                      <td key={sk.id} className="p-1.5 text-center">
                        <button
                          onClick={() =>
                            setEditingCell({
                              employeeId: emp.id,
                              skillId: sk.id,
                              employeeName: emp.name,
                              skillName: sk.name,
                              currentProficiency: prof,
                              currentTarget: target || null,
                            })
                          }
                          className={cn(
                            "w-full h-10 rounded-lg flex flex-col items-center justify-center transition-all hover:scale-105 hover:ring-2 hover:ring-indigo-400/50 border",
                            prof >= 4
                              ? "bg-indigo-50 border-indigo-200 text-indigo-900 dark:bg-indigo-950/50 dark:border-indigo-500/40 dark:text-indigo-200"
                              : prof > 0
                              ? "bg-slate-100 border-slate-200 text-slate-800 dark:bg-slate-800/70 dark:border-white/5 dark:text-slate-300"
                              : "bg-slate-50/50 border-dashed border-slate-200 text-slate-400 hover:border-slate-300 dark:bg-slate-900/30 dark:border-slate-800/80 dark:text-slate-600 dark:hover:border-slate-700"
                          )}
                        >
                          {prof > 0 ? (
                            <>
                              <span className="font-mono font-bold text-xs">
                                Lvl {prof}
                              </span>
                              {target && target > prof && (
                                <span className="flex items-center gap-0.5 text-[9px] text-purple-700 dark:text-purple-300 font-mono">
                                  <Star className="h-2 w-2 fill-purple-500 text-purple-500 dark:fill-purple-300 dark:text-purple-300" />
                                  T{target}
                                </span>
                              )}
                            </>
                          ) : (
                            <span className="text-[10px] text-slate-400 dark:text-slate-600">+</span>
                          )}
                        </button>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Modal: Edit Skill Proficiency & Target */}
      {editingCell && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-md rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 p-6 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-foreground">
            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">Update Skill Level</h3>
            <p className="text-xs text-muted-foreground mb-4">
              {editingCell.employeeName} &bull; <strong className="text-slate-900 dark:text-white">{editingCell.skillName}</strong>
            </p>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-medium mb-2">
                  Current Proficiency Level (1 to 5)
                </label>
                <div className="grid grid-cols-5 gap-2">
                  {[1, 2, 3, 4, 5].map((lvl) => (
                    <button
                      key={lvl}
                      type="button"
                      onClick={() =>
                        setEditingCell({ ...editingCell, currentProficiency: lvl })
                      }
                      className={cn(
                        "rounded-xl py-2.5 font-bold font-mono border text-center transition-all",
                        editingCell.currentProficiency === lvl
                          ? "bg-indigo-600 text-white border-indigo-500 shadow-md"
                          : "bg-slate-100 text-slate-800 border-slate-200 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-white/5 dark:hover:bg-slate-700"
                      )}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-medium mb-2">
                  Strategic Growth Target (Aspirational Level)
                </label>
                <div className="grid grid-cols-5 gap-2">
                  {[1, 2, 3, 4, 5].map((lvl) => (
                    <button
                      key={lvl}
                      type="button"
                      onClick={() =>
                        setEditingCell({ ...editingCell, currentTarget: lvl })
                      }
                      className={cn(
                        "rounded-xl py-2.5 font-bold font-mono border text-center transition-all",
                        editingCell.currentTarget === lvl
                          ? "bg-purple-600 text-white border-purple-500 shadow-md"
                          : "bg-slate-100 text-slate-800 border-slate-200 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-white/5 dark:hover:bg-slate-700"
                      )}
                    >
                      ★ {lvl}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-slate-200 dark:border-white/10 text-xs">
              <button
                onClick={() => setEditingCell(null)}
                className="rounded-xl px-4 py-2 text-muted-foreground hover:text-slate-900 dark:hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={() =>
                  handleSaveCell(
                    editingCell.currentProficiency,
                    editingCell.currentTarget
                  )
                }
                className="rounded-xl bg-indigo-600 px-4 py-2 font-semibold text-white shadow hover:bg-indigo-500 transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
