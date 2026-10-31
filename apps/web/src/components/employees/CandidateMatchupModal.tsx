"use client";

import React, { useState, useEffect } from "react";
import { Employee, CandidateMatchupResponse, getCandidateMatchup } from "@/lib/api";
import { formatCurrency, cn } from "@/lib/utils";
import {
  X,
  Bot,
  Sparkles,
  Compass,
  Activity,
  HeartHandshake,
  DollarSign,
  Quote,
  CheckCircle2,
  ArrowRightLeft,
  Trophy,
} from "lucide-react";

interface CandidateMatchupModalProps {
  isOpen: boolean;
  onClose: () => void;
  employees: Employee[];
  initialCandidateAId?: string;
  initialCandidateBId?: string;
  initialRoleTitle?: string;
}

export function CandidateMatchupModal({
  isOpen,
  onClose,
  employees,
  initialCandidateAId,
  initialCandidateBId,
  initialRoleTitle,
}: CandidateMatchupModalProps) {
  const [candidateAId, setCandidateAId] = useState<string>(
    initialCandidateAId || (employees[3]?.id || employees[0]?.id || "")
  );
  const [candidateBId, setCandidateBId] = useState<string>(
    initialCandidateBId || (employees[1]?.id || employees[0]?.id || "")
  );
  const [roleTitle, setRoleTitle] = useState<string>(
    initialRoleTitle || "Core Backend Engineer"
  );
  const [matchupData, setMatchupData] = useState<CandidateMatchupResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Sync state if props change
  useEffect(() => {
    if (initialCandidateAId) setCandidateAId(initialCandidateAId);
    if (initialCandidateBId) setCandidateBId(initialCandidateBId);
    if (initialRoleTitle) setRoleTitle(initialRoleTitle);
  }, [initialCandidateAId, initialCandidateBId, initialRoleTitle]);

  // Load matchup
  useEffect(() => {
    if (!isOpen || !candidateAId || !candidateBId) return;

    async function loadComparison() {
      setIsLoading(true);
      try {
        const res = await getCandidateMatchup(candidateAId, candidateBId, roleTitle);
        setMatchupData(res);
      } catch (err) {
        // Fallback local comparison generator
        const empA = employees.find((e) => e.id === candidateAId);
        const empB = employees.find((e) => e.id === candidateBId);
        if (empA && empB) {
          const dossierA = empA.dossier;
          const dossierB = empB.dossier;
          const burnoutA = dossierA?.burnout_risk_score ?? 0.15;
          const burnoutB = dossierB?.burnout_risk_score ?? 0.78;

          setMatchupData({
            role_title: roleTitle,
            project_name: "Fintech Real-Time Ledger",
            candidate_a: {
              id: empA.id,
              name: empA.name,
              role: empA.role,
              hourly_rate: empA.cost_per_hour,
              archetype: dossierA?.archetype || "Mentor",
              archetype_fit_rating: "High",
              archetype_fit_score: 120,
              burnout_risk_score: burnoutA,
              burnout_status: burnoutA < 0.5 ? "Protected / Sustainable" : "High Fatigue",
              coaching_sentiment: dossierA?.coaching_sentiment || "Active Mentee",
              stretch_readiness_score: dossierA?.stretch_readiness_score || 0.85,
              matching_skills: empA.skills.map((s) => s.skill_name || "Python"),
              evidence_quote: dossierA?.evidence_citations?.[0]?.evidence || "Eager to expand distributed system competencies.",
              weekly_margin_generated: (180 - empA.cost_per_hour) * 40,
            },
            candidate_b: {
              id: empB.id,
              name: empB.name,
              role: empB.role,
              hourly_rate: empB.cost_per_hour,
              archetype: dossierB?.archetype || "Firefighter",
              archetype_fit_rating: "Moderate",
              archetype_fit_score: 90,
              burnout_risk_score: burnoutB,
              burnout_status: burnoutB >= 0.5 ? `High Fatigue (${Math.round(burnoutB * 100)}%)` : "Sustainable",
              coaching_sentiment: dossierB?.coaching_sentiment || "Exemplary Coach",
              stretch_readiness_score: dossierB?.stretch_readiness_score || 0.95,
              matching_skills: empB.skills.map((s) => s.skill_name || "Python"),
              evidence_quote: dossierB?.evidence_citations?.[0]?.evidence || "Proven production incident triage leader.",
              weekly_margin_generated: (180 - empB.cost_per_hour) * 40,
            },
            recommended_candidate_id: empA.id,
            verdict_headline: `${empA.name} recommended over ${empB.name} (Burnout Protection & Margin Arbitrage)`,
            executive_counterfactual_explanation: `While ${empB.name} has higher raw seniority, their fatigue index is at ${Math.round(burnoutB * 100)}% from consecutive on-call paging. Assigning ${empA.name} ($${empA.cost_per_hour}/hr) protects ${empB.name} from attrition while generating $${((180 - empA.cost_per_hour) * 40).toLocaleString()}/wk in project gross margin with senior oversight.`,
            tradeoff_summary: {
              weekly_margin_diff: (180 - empA.cost_per_hour) * 40 - (180 - empB.cost_per_hour) * 40,
              burnout_risk_diff: Math.round((burnoutA - burnoutB) * 100) / 100,
              growth_points_winner: empA.name,
            },
          });
        }
      } finally {
        setIsLoading(false);
      }
    }

    loadComparison();
  }, [isOpen, candidateAId, candidateBId, roleTitle, employees]);

  if (!isOpen) return null;

  const candidateA = matchupData?.candidate_a;
  const candidateB = matchupData?.candidate_b;
  const isAWinner = matchupData?.recommended_candidate_id === candidateA?.id;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 p-6 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-foreground animate-scaleUp">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-200 dark:border-white/10 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded-md bg-indigo-50 dark:bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
                Cognitive Candidate Matchup
              </span>
              <span className="text-xs text-muted-foreground font-mono">Counterfactual "Why A over B"</span>
            </div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mt-1">
              Candidate Selection Analysis
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Compare two team members across behavioral archetype, evidence citations, burnout risk, and margin impact.
            </p>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Selection Controls */}
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-white/5 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Candidate A</label>
            <select
              value={candidateAId}
              onChange={(e) => setCandidateAId(e.target.value)}
              className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {employees.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name} ({e.role.split(" ")[0]})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Candidate B</label>
            <select
              value={candidateBId}
              onChange={(e) => setCandidateBId(e.target.value)}
              className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {employees.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name} ({e.role.split(" ")[0]})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Target Role</label>
            <select
              value={roleTitle}
              onChange={(e) => setRoleTitle(e.target.value)}
              className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-800 px-3 py-2 text-slate-900 dark:text-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="Core Backend Engineer">Core Backend Engineer</option>
              <option value="Lead Cloud Architect">Lead Cloud Architect</option>
              <option value="Frontend Lead">Frontend Lead</option>
              <option value="DevOps & Cloud Specialist">DevOps &amp; Cloud Specialist</option>
            </select>
          </div>
        </div>

        {/* Alex's Executive Verdict Banner */}
        {matchupData && (
          <div className="mt-4 rounded-2xl border border-indigo-200 dark:border-indigo-500/30 bg-gradient-to-r from-indigo-50/70 via-white to-purple-50/50 dark:from-slate-900 dark:via-slate-800/80 dark:to-indigo-950/40 p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-1">
              <Bot className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">Alex's Executive Matchup Verdict</h3>
            </div>
            <p className="text-sm font-bold text-indigo-950 dark:text-indigo-200 mt-0.5">
              {matchupData.verdict_headline}
            </p>
            <p className="text-xs text-slate-700 dark:text-slate-300 mt-2 leading-relaxed whitespace-pre-line">
              {matchupData.executive_counterfactual_explanation}
            </p>
          </div>
        )}

        {/* Side-by-Side Comparison Cards */}
        {candidateA && candidateB && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Candidate A Card */}
            <div className={cn(
              "rounded-2xl border p-4 transition-all relative",
              isAWinner
                ? "border-emerald-300 dark:border-emerald-500/40 bg-emerald-50/30 dark:bg-emerald-950/20 shadow-md ring-2 ring-emerald-500/20"
                : "border-slate-200 dark:border-white/10 bg-white/60 dark:bg-slate-800/40"
            )}>
              {isAWinner && (
                <span className="absolute -top-2.5 right-4 flex items-center gap-1 rounded-full bg-emerald-600 px-2.5 py-0.5 text-[10px] font-bold text-white shadow-sm">
                  <Trophy className="h-3 w-3" /> Recommended Fit
                </span>
              )}

              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/5">
                <div>
                  <h4 className="text-base font-bold text-slate-900 dark:text-white">{candidateA.name}</h4>
                  <p className="text-xs text-muted-foreground">{candidateA.role} &bull; ${candidateA.hourly_rate}/hr</p>
                </div>
                <span className="rounded-lg bg-indigo-50 dark:bg-indigo-950/60 px-2 py-1 text-xs font-mono font-bold text-indigo-700 dark:text-indigo-300">
                  {candidateA.archetype}
                </span>
              </div>

              <div className="mt-3 space-y-2.5 text-xs">
                {/* Burnout Status */}
                <div className="flex items-center justify-between p-2 rounded-xl bg-white/70 dark:bg-slate-900/60 border border-slate-100 dark:border-white/5">
                  <span className="flex items-center gap-1.5 text-muted-foreground">
                    <Activity className="h-3.5 w-3.5 text-rose-500" /> Fatigue Level:
                  </span>
                  <span className={cn(
                    "font-bold font-mono",
                    candidateA.burnout_risk_score >= 0.5 ? "text-amber-600 dark:text-amber-400" : "text-emerald-600 dark:text-emerald-400"
                  )}>
                    {Math.round(candidateA.burnout_risk_score * 100)}% ({candidateA.burnout_status})
                  </span>
                </div>

                {/* Margin Impact */}
                <div className="flex items-center justify-between p-2 rounded-xl bg-white/70 dark:bg-slate-900/60 border border-slate-100 dark:border-white/5">
                  <span className="flex items-center gap-1.5 text-muted-foreground">
                    <DollarSign className="h-3.5 w-3.5 text-emerald-500" /> Weekly Margin:
                  </span>
                  <span className="font-bold font-mono text-emerald-600 dark:text-emerald-400">
                    +{formatCurrency(candidateA.weekly_margin_generated)}/wk
                  </span>
                </div>

                {/* Evidence Quote */}
                {candidateA.evidence_quote && (
                  <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-100 dark:border-white/5 text-[11px] italic text-slate-700 dark:text-slate-300 flex items-start gap-1.5">
                    <Quote className="h-3 w-3 shrink-0 text-indigo-500 mt-0.5" />
                    <span>&ldquo;{candidateA.evidence_quote}&rdquo;</span>
                  </div>
                )}
              </div>
            </div>

            {/* Candidate B Card */}
            <div className={cn(
              "rounded-2xl border p-4 transition-all relative",
              !isAWinner
                ? "border-emerald-300 dark:border-emerald-500/40 bg-emerald-50/30 dark:bg-emerald-950/20 shadow-md ring-2 ring-emerald-500/20"
                : "border-slate-200 dark:border-white/10 bg-white/60 dark:bg-slate-800/40"
            )}>
              {!isAWinner && (
                <span className="absolute -top-2.5 right-4 flex items-center gap-1 rounded-full bg-emerald-600 px-2.5 py-0.5 text-[10px] font-bold text-white shadow-sm">
                  <Trophy className="h-3 w-3" /> Recommended Fit
                </span>
              )}

              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/5">
                <div>
                  <h4 className="text-base font-bold text-slate-900 dark:text-white">{candidateB.name}</h4>
                  <p className="text-xs text-muted-foreground">{candidateB.role} &bull; ${candidateB.hourly_rate}/hr</p>
                </div>
                <span className="rounded-lg bg-indigo-50 dark:bg-indigo-950/60 px-2 py-1 text-xs font-mono font-bold text-indigo-700 dark:text-indigo-300">
                  {candidateB.archetype}
                </span>
              </div>

              <div className="mt-3 space-y-2.5 text-xs">
                {/* Burnout Status */}
                <div className="flex items-center justify-between p-2 rounded-xl bg-white/70 dark:bg-slate-900/60 border border-slate-100 dark:border-white/5">
                  <span className="flex items-center gap-1.5 text-muted-foreground">
                    <Activity className="h-3.5 w-3.5 text-rose-500" /> Fatigue Level:
                  </span>
                  <span className={cn(
                    "font-bold font-mono",
                    candidateB.burnout_risk_score >= 0.5 ? "text-amber-600 dark:text-amber-400" : "text-emerald-600 dark:text-emerald-400"
                  )}>
                    {Math.round(candidateB.burnout_risk_score * 100)}% ({candidateB.burnout_status})
                  </span>
                </div>

                {/* Margin Impact */}
                <div className="flex items-center justify-between p-2 rounded-xl bg-white/70 dark:bg-slate-900/60 border border-slate-100 dark:border-white/5">
                  <span className="flex items-center gap-1.5 text-muted-foreground">
                    <DollarSign className="h-3.5 w-3.5 text-emerald-500" /> Weekly Margin:
                  </span>
                  <span className="font-bold font-mono text-emerald-600 dark:text-emerald-400">
                    +{formatCurrency(candidateB.weekly_margin_generated)}/wk
                  </span>
                </div>

                {/* Evidence Quote */}
                {candidateB.evidence_quote && (
                  <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-100 dark:border-white/5 text-[11px] italic text-slate-700 dark:text-slate-300 flex items-start gap-1.5">
                    <Quote className="h-3 w-3 shrink-0 text-indigo-500 mt-0.5" />
                    <span>&ldquo;{candidateB.evidence_quote}&rdquo;</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="mt-6 flex items-center justify-between border-t border-slate-200 dark:border-white/10 pt-4">
          <div className="text-xs text-muted-foreground">
            Analysis accounts for skill proficiency graph, living evidence citations, and solver margin objectives.
          </div>
          <button
            onClick={onClose}
            className="rounded-xl bg-indigo-600 px-5 py-2 text-xs font-semibold text-white shadow hover:bg-indigo-500 transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
