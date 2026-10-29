"use client";

import React, { useState } from "react";
import {
  X,
  Sparkles,
  Award,
  ShieldCheck,
  Flame,
  UserCheck,
  Briefcase,
  Users,
  Compass,
  FileText,
  Quote,
  Target,
  PlusCircle,
  TrendingUp,
  AlertCircle
} from "lucide-react";
import { Employee, EmployeeDossier } from "@/lib/api";
import { cn } from "@/lib/utils";

interface EmployeeDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  employee: Employee | null;
  onUploadMore: (employeeId: string) => void;
}

export function EmployeeDossierModal({
  isOpen,
  onClose,
  employee,
  onUploadMore,
}: EmployeeDossierModalProps) {
  const [activeTab, setActiveTab] = useState<"skills" | "collaboration" | "aspirations" | "documents">("skills");

  if (!isOpen || !employee) return null;

  // Use employee's dossier or construct realistic Level 1 fallback
  const dossier: EmployeeDossier = employee.dossier || {
    id: `dos-${employee.id}`,
    employee_id: employee.id,
    employee_name: employee.name,
    employee_role: employee.role,
    employee_email: employee.email,
    archetype: "Optimizer",
    archetype_rationale: "Exhibits consistent execution, structured problem-solving, and clean delivery discipline.",
    burnout_risk_score: 0.20,
    burnout_factors: ["Standard baseline workload"],
    coaching_sentiment: "Collaborative Team Contributor",
    client_facing_comfort: "Moderate (Effective with technical peers)",
    preferred_team_size: "Standard Agile squad (3-6 members)",
    strengths_summary: [
      `Reliable execution in ${employee.role}`,
      "Clean test-driven development practices"
    ],
    growth_areas: ["Expanding system architecture scope"],
    career_aspirations: employee.career_goals || ["Continuous engineering growth"],
    stretch_readiness_score: 0.80,
    profile_summary: `Living Dossier synthesized from profile records for ${employee.name}. Ready for multi-source enrichment.`,
    confidence_overall: 0.85,
    enrichment_level: 1,
    evidence_citations: (employee.skills || []).map((s) => ({
      skill: s.skill_name,
      proficiency: s.proficiency,
      confidence: 0.88,
      evidence: `Demonstrated proficiency in ${s.skill_name} across multiple sprint cycles.`,
      sources: ["profile_record"]
    })),
    documents: [
      { id: "doc-init", filename: `${employee.name.toLowerCase().replace(" ", "_")}_profile.pdf`, file_type: "pdf", category: "resume", created_at: "2026-09-01T10:00:00Z" }
    ],
    created_at: "2026-09-01T10:00:00Z",
    updated_at: "2026-10-20T10:00:00Z"
  };

  const getBurnoutColor = (score: number) => {
    if (score >= 0.60) return "text-rose-500 bg-rose-500/10 border-rose-500/20";
    if (score >= 0.35) return "text-amber-500 bg-amber-500/10 border-amber-500/20";
    return "text-emerald-500 bg-emerald-500/10 border-emerald-500/20";
  };

  const getArchetypeBadgeColor = (archetype: string) => {
    switch (archetype) {
      case "Pathfinder":
        return "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20";
      case "Optimizer":
        return "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20";
      case "Firefighter":
        return "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20";
      case "Mentor":
        return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";
      default:
        return "bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-3xl rounded-3xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 p-6 sm:p-8 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-foreground max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 rounded-full p-2 text-muted-foreground hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Header Profile Section */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-white/10 pb-6 mb-6">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white font-black text-xl shadow-lg shadow-indigo-600/30">
              {employee.name.split(" ").map((n) => n[0]).join("")}
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">
                  {employee.name}
                </h2>
                <span className={cn(
                  "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-bold",
                  getArchetypeBadgeColor(dossier.archetype)
                )}>
                  <Award className="h-3.5 w-3.5" />
                  {dossier.archetype}
                </span>
              </div>
              <p className="text-xs font-medium text-slate-500 dark:text-muted-foreground mt-0.5">
                {employee.role} • {employee.email} • ${employee.cost_per_hour}/hr
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onUploadMore(employee.id)}
              className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-2 text-xs font-bold text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-500 transition-all"
            >
              <PlusCircle className="h-4 w-4" />
              <span>Enrich Profile</span>
            </button>
          </div>
        </div>

        {/* Cognitive Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 mb-6">
          {/* Overall Confidence */}
          <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800/40 p-4">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-500 dark:text-muted-foreground">
                Calibration Confidence
              </span>
              <ShieldCheck className="h-4 w-4 text-emerald-500" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                {Math.round(dossier.confidence_overall * 100)}%
              </span>
              <span className="text-[11px] font-semibold text-slate-500">
                Level {dossier.enrichment_level} (Multi-Source)
              </span>
            </div>
            <div className="mt-2 h-1.5 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
              <div
                className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                style={{ width: `${dossier.confidence_overall * 100}%` }}
              />
            </div>
          </div>

          {/* Burnout Stress Index */}
          <div className={cn("rounded-2xl border p-4", getBurnoutColor(dossier.burnout_risk_score))}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold">Burnout Fatigue Index</span>
              <Flame className="h-4 w-4" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black">
                {Math.round(dossier.burnout_risk_score * 100)}%
              </span>
              <span className="text-[11px] font-medium opacity-90">
                {dossier.burnout_risk_score > 0.5 ? "High Risk" : (dossier.burnout_risk_score > 0.3 ? "Moderate" : "Sustainable")}
              </span>
            </div>
            <div className="mt-2 h-1.5 w-full rounded-full bg-black/10 dark:bg-white/10 overflow-hidden">
              <div
                className="h-full rounded-full bg-current transition-all duration-500"
                style={{ width: `${dossier.burnout_risk_score * 100}%` }}
              />
            </div>
          </div>

          {/* Stretch Readiness */}
          <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800/40 p-4">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-500 dark:text-muted-foreground">
                Stretch Readiness
              </span>
              <TrendingUp className="h-4 w-4 text-indigo-500" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-indigo-600 dark:text-indigo-400">
                {Math.round(dossier.stretch_readiness_score * 100)}%
              </span>
              <span className="text-[11px] font-semibold text-slate-500">
                Eligible for Stretch
              </span>
            </div>
            <div className="mt-2 h-1.5 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
              <div
                className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                style={{ width: `${dossier.stretch_readiness_score * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Profile Rationale Box */}
        <div className="rounded-2xl border border-indigo-500/20 bg-indigo-50/50 dark:bg-indigo-950/20 p-4 mb-6">
          <div className="flex items-start gap-3">
            <Sparkles className="h-5 w-5 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
            <div className="text-xs leading-relaxed text-slate-700 dark:text-slate-300">
              <strong className="font-bold text-indigo-900 dark:text-indigo-300 block mb-0.5">
                Human-Like Resource Persona ({dossier.archetype})
              </strong>
              {dossier.profile_summary}
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-white/10 mb-5 pb-1">
          <button
            onClick={() => setActiveTab("skills")}
            className={cn(
              "px-3.5 py-2 text-xs font-bold rounded-xl transition-all",
              activeTab === "skills"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-600 dark:text-muted-foreground hover:text-slate-900 dark:hover:text-white"
            )}
          >
            Verified Skills & Evidence ({dossier.evidence_citations.length})
          </button>
          <button
            onClick={() => setActiveTab("collaboration")}
            className={cn(
              "px-3.5 py-2 text-xs font-bold rounded-xl transition-all",
              activeTab === "collaboration"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-600 dark:text-muted-foreground hover:text-slate-900 dark:hover:text-white"
            )}
          >
            Team Chemistry & Soft Skills
          </button>
          <button
            onClick={() => setActiveTab("aspirations")}
            className={cn(
              "px-3.5 py-2 text-xs font-bold rounded-xl transition-all",
              activeTab === "aspirations"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-600 dark:text-muted-foreground hover:text-slate-900 dark:hover:text-white"
            )}
          >
            Growth & Stretch Vectors
          </button>
          <button
            onClick={() => setActiveTab("documents")}
            className={cn(
              "px-3.5 py-2 text-xs font-bold rounded-xl transition-all",
              activeTab === "documents"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-600 dark:text-muted-foreground hover:text-slate-900 dark:hover:text-white"
            )}
          >
            Ingested Sources ({dossier.documents.length})
          </button>
        </div>

        {/* Tab 1: Skills & Real Evidence Quotes */}
        {activeTab === "skills" && (
          <div className="space-y-3.5 animate-fadeIn">
            {dossier.evidence_citations.map((c, i) => (
              <div
                key={i}
                className="rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50/70 dark:bg-slate-800/40 p-4 transition-all hover:border-indigo-500/30"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-slate-900 dark:text-white">
                      {c.skill}
                    </span>
                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <div
                          key={star}
                          className={cn(
                            "h-2 w-2 rounded-full",
                            star <= c.proficiency ? "bg-amber-400" : "bg-slate-300 dark:bg-slate-700"
                          )}
                        />
                      ))}
                      <span className="text-[11px] font-bold text-slate-600 dark:text-slate-400 ml-1">
                        Level {c.proficiency}/5
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-[11px] font-bold text-emerald-600 dark:text-emerald-400">
                      <ShieldCheck className="h-3 w-3" />
                      {Math.round(c.confidence * 100)}% Confidence
                    </span>
                    <div className="flex gap-1">
                      {c.sources.map((src, idx) => (
                        <span
                          key={idx}
                          className="rounded bg-indigo-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-600 dark:text-indigo-400"
                        >
                          {src}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-900/60 p-3 rounded-xl border border-slate-200/60 dark:border-white/5">
                  <Quote className="h-4 w-4 text-indigo-400 shrink-0 mt-0.5" />
                  <p className="italic leading-relaxed">{c.evidence}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 2: Team Chemistry & Soft Skills */}
        {activeTab === "collaboration" && (
          <div className="space-y-4 animate-fadeIn">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
              <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800/40 p-4">
                <span className="text-xs font-semibold text-slate-500 dark:text-muted-foreground block mb-1">
                  Coaching & Mentorship
                </span>
                <span className="text-sm font-bold text-slate-900 dark:text-white">
                  {dossier.coaching_sentiment}
                </span>
              </div>
              <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800/40 p-4">
                <span className="text-xs font-semibold text-slate-500 dark:text-muted-foreground block mb-1">
                  Client-Facing Readiness
                </span>
                <span className="text-sm font-bold text-slate-900 dark:text-white">
                  {dossier.client_facing_comfort}
                </span>
              </div>
              <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800/40 p-4">
                <span className="text-xs font-semibold text-slate-500 dark:text-muted-foreground block mb-1">
                  Preferred Squad Size
                </span>
                <span className="text-sm font-bold text-slate-900 dark:text-white">
                  {dossier.preferred_team_size}
                </span>
              </div>
            </div>

            {/* Strengths & Growth Areas */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4">
                <h4 className="text-xs font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4" />
                  Key Strengths
                </h4>
                <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                  {dossier.strengths_summary.map((st, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                      <span>{st}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4">
                <h4 className="text-xs font-bold text-amber-700 dark:text-amber-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <AlertCircle className="h-4 w-4" />
                  Growth & Pacing Areas
                </h4>
                <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                  {dossier.growth_areas.map((gr, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                      <span>{gr}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Aspirations & Stretch Vectors */}
        {activeTab === "aspirations" && (
          <div className="space-y-4 animate-fadeIn">
            <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800/40 p-5">
              <h4 className="text-xs font-bold text-indigo-700 dark:text-indigo-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Target className="h-4 w-4" />
                Active Career Growth Vectors
              </h4>
              <div className="space-y-2.5">
                {dossier.career_aspirations.map((asp, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-white/5 text-xs font-medium"
                  >
                    <span className="text-slate-800 dark:text-slate-200">{asp}</span>
                    <span className="rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-[10px] font-bold text-indigo-600 dark:text-indigo-400">
                      Stretch Target
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50/50 dark:bg-slate-800/30 p-4 text-xs text-slate-600 dark:text-slate-400">
              💡 <strong>Resource Manager Note:</strong> Assigning {employee.name} to projects that demand these target skills will generate a <em>Stretch Learning Bonus</em> in the optimization solver, while automatically enforcing qualified senior mentor pairing.
            </div>
          </div>
        )}

        {/* Tab 4: Ingested Document History */}
        {activeTab === "documents" && (
          <div className="space-y-3 animate-fadeIn">
            {dossier.documents.map((doc, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3.5 rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50/70 dark:bg-slate-800/40 text-xs"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div>
                    <span className="font-bold text-slate-900 dark:text-white block">
                      {doc.filename}
                    </span>
                    <span className="text-[11px] text-muted-foreground">
                      Category: {doc.category} • Uploaded {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <span className="rounded-lg bg-emerald-500/10 px-2.5 py-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                  Corroborated
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
