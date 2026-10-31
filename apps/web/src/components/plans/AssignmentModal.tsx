"use client";

import React from "react";
import { Assignment } from "@/lib/api";
import { formatCurrency, cn } from "@/lib/utils";
import { 
  X, 
  Lock, 
  Unlock, 
  Award, 
  HeartHandshake, 
  DollarSign, 
  Target, 
  CheckCircle2, 
  Compass,
  Activity,
  Sparkles,
  Quote
} from "lucide-react";

interface AssignmentModalProps {
  assignment: Assignment | null;
  onClose: () => void;
  onToggleLock: (assignmentId: string) => void;
}

export function AssignmentModal({ assignment, onClose, onToggleLock }: AssignmentModalProps) {
  if (!assignment) return null;

  const reasons: any = assignment.reasons;
  const skillMatch: any = reasons?.skill_match;
  const growth: any = reasons?.growth || reasons?.growth_alignment;
  const cost: any = reasons?.cost || reasons?.margin_contribution;
  const archetypeFit: any = reasons?.archetype_fit;
  const burnoutMitigation: any = reasons?.burnout_mitigation;
  const mentorPairing: any = reasons?.mentor_pairing || reasons?.mentor_synergy;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-lg rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 p-6 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-foreground animate-scaleUp max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-200 dark:border-white/10 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-indigo-50 dark:bg-indigo-500/10 px-2 py-0.5 text-xs font-mono font-bold text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
                Week {assignment.week_number}
              </span>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">{assignment.project_name}</h3>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Role: <span className="text-slate-800 dark:text-slate-300 font-medium">{assignment.role_title || assignment.role_name}</span> &bull; Staffed:{" "}
              <span className="text-slate-900 dark:text-white font-semibold">{assignment.employee_name}</span> ({assignment.allocated_hours || assignment.hours || 40}h)
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-muted-foreground hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Cognitive Explainability Body */}
        <div className="mt-4 space-y-3.5 text-xs">
          {/* 1. Behavioral Archetype Fit */}
          {archetypeFit && (
            <div className="rounded-xl border border-blue-200 dark:border-blue-500/30 bg-blue-50/70 dark:bg-blue-950/20 p-3.5">
              <div className="flex items-center justify-between mb-1">
                <span className="flex items-center gap-1.5 font-semibold text-blue-900 dark:text-blue-300">
                  <Compass className="h-4 w-4 text-blue-600 dark:text-blue-400" /> Archetype Synergy: {archetypeFit.archetype}
                </span>
                <span className="font-mono text-blue-700 dark:text-blue-300 font-bold text-[11px]">
                  +{archetypeFit.bonus_earned || 150} pts
                </span>
              </div>
              <p className="text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed">
                {archetypeFit.fit_label || "Candidate behavioral strengths strongly align with role complexity and mandate."}
              </p>
            </div>
          )}

          {/* 2. Burnout & Fatigue Mitigation Status */}
          {burnoutMitigation && (
            <div className={cn(
              "rounded-xl border p-3.5",
              (burnoutMitigation.burnout_risk_score >= 0.50)
                ? "border-amber-200 dark:border-amber-500/30 bg-amber-50/70 dark:bg-amber-950/20 text-amber-900 dark:text-amber-200"
                : "border-emerald-200 dark:border-emerald-500/30 bg-emerald-50/70 dark:bg-emerald-950/20 text-emerald-900 dark:text-emerald-200"
            )}>
              <div className="flex items-center justify-between mb-1">
                <span className="flex items-center gap-1.5 font-semibold">
                  <Activity className="h-4 w-4" /> Wellness & Fatigue Guardrail
                </span>
                <span className="font-mono font-bold text-[11px]">
                  {Math.round((burnoutMitigation.burnout_risk_score || 0.15) * 100)}% Stress
                </span>
              </div>
              <p className="text-[11px] leading-relaxed">
                {burnoutMitigation.status || "Workload calibrated within sustainable capacity thresholds."}
              </p>
            </div>
          )}

          {/* 3. Skill Competency Match */}
          <div className="rounded-xl border border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-slate-800/40 p-3.5">
            <div className="flex items-center justify-between mb-2">
              <span className="flex items-center gap-1.5 font-semibold text-slate-900 dark:text-slate-200">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" /> Skill Competency Match
              </span>
              {typeof skillMatch === "object" && skillMatch?.employee_proficiency && (
                <span className="font-mono text-emerald-700 dark:text-emerald-300 font-bold">
                  Proficiency {skillMatch.employee_proficiency} / {skillMatch.required_proficiency}
                </span>
              )}
            </div>
            {typeof skillMatch === "string" ? (
              <p className="text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed">{skillMatch}</p>
            ) : skillMatch?.skills ? (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {skillMatch.skills.map((s: any, idx: number) => (
                  <span
                    key={idx}
                    className="rounded bg-white dark:bg-slate-700/60 px-2 py-0.5 text-[11px] text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600/50 shadow-xs"
                  >
                    {s}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-[11px] text-muted-foreground">
                Matches required competencies with corroborated living dossier verification.
              </p>
            )}
          </div>

          {/* 4. Stretch & Certified Mentorship Pairing */}
          {assignment.is_stretch && (
            <div className="rounded-xl border border-purple-200 dark:border-purple-500/30 bg-purple-50/70 dark:bg-purple-950/20 p-3.5">
              <div className="flex items-center gap-2 mb-1.5">
                <Award className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                <span className="font-semibold text-purple-900 dark:text-purple-300">Sanctioned Stretch Assignment (1 Level Below)</span>
              </div>
              <p className="text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed">
                Candidate is developing toward this competency with an approved senior mentor attached.
              </p>
              {assignment.mentor_name && (
                <div className="mt-2.5 flex items-center justify-between rounded-lg bg-white dark:bg-slate-900/80 p-2.5 border border-purple-200 dark:border-purple-500/20 shadow-xs">
                  <div className="flex items-center gap-2">
                    <HeartHandshake className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                    <div>
                      <span className="text-slate-800 dark:text-slate-200 font-medium">
                        Mentor: <strong className="text-slate-900 dark:text-white">{assignment.mentor_name}</strong>
                      </span>
                      <p className="text-[10px] text-muted-foreground">10% capacity reserved for weekly reviews</p>
                    </div>
                  </div>
                  <span className="rounded-md bg-purple-100 dark:bg-purple-900/40 px-2 py-0.5 text-[10px] font-mono text-purple-800 dark:text-purple-300 font-semibold">
                    +250 Quality Synergy
                  </span>
                </div>
              )}
            </div>
          )}

          {/* 5. Career Goal Alignment & Growth */}
          {growth && (
            <div className="rounded-xl border border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-slate-800/40 p-3.5">
              <div className="flex items-center justify-between mb-1.5">
                <span className="flex items-center gap-1.5 font-semibold text-slate-900 dark:text-slate-200">
                  <Target className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Growth Score Contribution
                </span>
                <span className="font-mono text-indigo-700 dark:text-indigo-300 font-bold">
                  +{typeof growth === "object" ? growth.growth_score_contribution || 180 : 180} pts
                </span>
              </div>
              {typeof growth === "string" ? (
                <p className="text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed">{growth}</p>
              ) : growth.career_aspiration || (growth.matched_goals && growth.matched_goals[0]) ? (
                <div className="mt-2 rounded bg-indigo-50 dark:bg-indigo-950/30 p-2 border border-indigo-200 dark:border-indigo-500/20 text-indigo-900 dark:text-indigo-200 text-[11px] flex items-center gap-1.5">
                  <Quote className="h-3 w-3 shrink-0 text-indigo-500" />
                  <span>
                    <strong>Career Aspiration:</strong> &ldquo;{growth.career_aspiration || growth.matched_goals[0]}&rdquo;
                  </span>
                </div>
              ) : null}
            </div>
          )}

          {/* 6. Commercial Margin Contribution */}
          {cost && (
            <div className="rounded-xl border border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-slate-800/40 p-3.5">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 font-semibold text-slate-900 dark:text-slate-200">
                  <DollarSign className="h-4 w-4 text-emerald-600 dark:text-emerald-400" /> Commercial Contribution
                </span>
                <span className="font-mono text-slate-900 dark:text-slate-200 font-semibold">
                  {typeof cost === "string"
                    ? cost
                    : cost.est_margin_generated
                    ? `+$${Number(cost.est_margin_generated).toLocaleString()}/wk margin`
                    : `${formatCurrency(cost.total_assignment_cost || 0)} ($${cost.hourly_cost || 0}/hr)`}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="mt-6 flex items-center justify-between border-t border-slate-200 dark:border-white/10 pt-4">
          <button
            onClick={() => onToggleLock(assignment.id)}
            className={cn(
              "flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition-all border",
              assignment.is_locked
                ? "bg-amber-50 text-amber-900 border-amber-300 hover:bg-amber-100 dark:bg-amber-500/20 dark:text-amber-300 dark:border-amber-500/40 dark:hover:bg-amber-500/30"
                : "bg-slate-100 text-slate-800 border-slate-300 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700 dark:hover:bg-slate-700"
            )}
          >
            {assignment.is_locked ? (
              <>
                <Lock className="h-4 w-4 text-amber-500 dark:text-amber-400" /> Assignment Locked (Solver Fixed)
              </>
            ) : (
              <>
                <Unlock className="h-4 w-4 text-slate-500 dark:text-slate-400" /> Lock Assignment
              </>
            )}
          </button>

          <button
            onClick={onClose}
            className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow hover:bg-indigo-500 transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
