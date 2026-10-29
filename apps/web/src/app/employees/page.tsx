"use client";

import React, { useState } from "react";
import { MOCK_EMPLOYEES } from "@/lib/mockData";
import { Employee } from "@/lib/api";
import { CsvImportModal } from "@/components/data/CsvImportModal";
import { formatCurrency } from "@/lib/utils";
import { 
  Plus, 
  Upload, 
  Search, 
  Target, 
  CheckCircle2,
  Clock
} from "lucide-react";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>(MOCK_EMPLOYEES);
  const [searchQuery, setSearchQuery] = useState("");
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  // New employee form state
  const [newName, setNewName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState("Fullstack Engineer");
  const [newCost, setNewCost] = useState(80);
  const [newCapacity, setNewCapacity] = useState(40);
  const [newGoals, setNewGoals] = useState("");

  const filteredEmployees = employees.filter(
    (e) =>
      e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.role.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
    };

    setEmployees([newEmp, ...employees]);
    setShowAddModal(false);
    setNewName("");
    setNewEmail("");
    setNewGoals("");
    setNotification(`Employee "${newEmp.name}" added successfully.`);
    setTimeout(() => setNotification(null), 4000);
  };

  const handleImportSuccess = (count: number) => {
    setNotification(`Successfully imported ${count} employees from CSV with verified skill schema.`);
    setTimeout(() => setNotification(null), 4000);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="rounded-md bg-indigo-50 dark:bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
              Talent Pool & Capacity
            </span>
            <span className="text-xs text-muted-foreground">{employees.length} Engineers</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Employee Roster</h1>
          <p className="text-xs text-muted-foreground mt-1">
            Maintain employee skill proficiencies, hourly costs, weekly capacities, and growth targets.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setIsImportModalOpen(true)}
            id="import-employees-btn"
            className="flex items-center gap-2 rounded-xl bg-white dark:bg-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors shadow-sm"
          >
            <Upload className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            Import CSV
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            id="add-employee-btn"
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-indigo-600/20 hover:bg-indigo-500 transition-colors"
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

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search by name, role, or title..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/80 pl-10 pr-4 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
        />
      </div>

      {/* Employees Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredEmployees.map((emp) => (
          <div
            key={emp.id}
            className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl transition-all hover:border-indigo-500/40 hover:shadow-md dark:hover:shadow-xl shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 font-bold ring-1 ring-indigo-500/20">
                  {emp.name.split(" ").map((n) => n[0]).join("")}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{emp.name}</h3>
                  <p className="text-xs text-muted-foreground">{emp.role}</p>
                </div>
              </div>
              <span className="rounded-md bg-emerald-50 dark:bg-emerald-500/10 px-2 py-0.5 text-[10px] font-mono font-semibold text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20">
                {formatCurrency(emp.cost_per_hour)}/h
              </span>
            </div>

            {/* Capacity & Overtime specs */}
            <div className="mt-4 flex items-center justify-between rounded-xl bg-slate-50 dark:bg-slate-800/40 p-2.5 border border-slate-200 dark:border-white/5 text-xs text-slate-700 dark:text-slate-300 font-mono">
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <Clock className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" /> Standard: {emp.weekly_capacity_hours}h/w
              </span>
              <span>Max OT: +{emp.max_overtime_hours}h</span>
            </div>

            {/* Career Growth Goal */}
            {emp.career_goals.length > 0 && (
              <div className="mt-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/20 p-2.5 border border-indigo-200 dark:border-indigo-500/20 text-xs">
                <div className="flex items-center gap-1.5 text-indigo-700 dark:text-indigo-300 font-semibold mb-1">
                  <Target className="h-3.5 w-3.5" /> Career Growth Goal
                </div>
                <p className="text-[11px] text-slate-700 dark:text-slate-300 italic leading-snug">
                  &ldquo;{emp.career_goals[0]}&rdquo;
                </p>
              </div>
            )}

            {/* Skills */}
            <div className="mt-4 border-t border-slate-200 dark:border-white/5 pt-3">
              <div className="flex items-center justify-between mb-2 text-xs">
                <span className="text-muted-foreground">Verified Skills & Targets</span>
                <span className="text-[10px] text-slate-500">Proficiency / Target</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {emp.skills.map((s) => (
                  <span
                    key={s.id}
                    className="flex items-center gap-1 rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-[11px] text-slate-800 dark:text-slate-300 border border-slate-200 dark:border-white/5"
                  >
                    <span>{s.skill_name}</span>
                    <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">P{s.proficiency}</span>
                    {s.growth_target && (
                      <span className="text-[10px] text-purple-600 dark:text-purple-300 font-mono flex items-center">
                        &rarr;T{s.growth_target}
                      </span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* CSV Import Modal */}
      <CsvImportModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        entityName="Employees & Skills"
        onSuccess={handleImportSuccess}
      />

      {/* Add Employee Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-lg rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 p-6 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-foreground">
            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">Add New Engineer</h3>
            <p className="text-xs text-muted-foreground mb-4">
              Register employee capacity, cost basis, and strategic career growth goals.
            </p>

            <form onSubmit={handleCreateEmployee} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Maya Chen"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Email</label>
                  <input
                    type="email"
                    required
                    placeholder="e.g. maya@acme.com"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Role</label>
                  <input
                    type="text"
                    required
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Hourly Cost ($)</label>
                  <input
                    type="number"
                    min="20"
                    max="300"
                    value={newCost}
                    onChange={(e) => setNewCost(parseInt(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Weekly Cap (h)</label>
                  <input
                    type="number"
                    min="10"
                    max="60"
                    value={newCapacity}
                    onChange={(e) => setNewCapacity(parseInt(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Career Growth Goal</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Lead system architecture on distributed systems..."
                  value={newGoals}
                  onChange={(e) => setNewGoals(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
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
                  Save Engineer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
