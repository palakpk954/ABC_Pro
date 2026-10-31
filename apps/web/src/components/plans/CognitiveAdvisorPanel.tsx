"use client";

import React from "react";
import { CognitiveAdvisory } from "@/lib/api";
import { formatCurrency, cn } from "@/lib/utils";
import {
  Sparkles,
  Bot,
  TrendingUp,
  HeartHandshake,
  Activity,
  Compass,
  MessageSquare,
  ChevronRight,
  ShieldAlert,
  AlertTriangle,
  Lightbulb,
} from "lucide-react";

interface CognitiveAdvisorPanelProps {
  advisory: CognitiveAdvisory;
  onOpenChat: (initialPrompt?: string) => void;
}

export function CognitiveAdvisorPanel({ advisory, onOpenChat }: CognitiveAdvisorPanelProps) {
  const { commercial_health, people_and_chemistry, strategic_recommendations } = advisory;

  const quickPrompts = [
    "Why did you assign Devon to the Fintech project?",
    "How is Marcus's burnout risk being protected?",
    "What would happen if we prioritize margin to 90%?",
  ];

  return (
    <div className="rounded-2xl border border-indigo-200/80 dark:border-indigo-500/20 bg-gradient-to-br from-indigo-50/70 via-white to-purple-50/50 dark:from-slate-900/90 dark:via-slate-900/60 dark:to-indigo-950/30 p-6 backdrop-blur-xl shadow-md dark:shadow-2xl transition-all">
      {/* Top Banner & Alex Badge */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-indigo-100 dark:border-white/10">
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center h-12 w-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/25">
            <Bot className="h-6 w-6" />
            <span className="absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 ring-2 ring-white dark:ring-slate-900">
              <Sparkles className="h-2.5 w-2.5 text-white" />
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">
                {advisory.advisor_name}
              </h2>
              <span className="rounded-full bg-indigo-100 dark:bg-indigo-500/20 px-2.5 py-0.5 text-[10px] font-mono font-semibold text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30">
                Cognitive RM Partner
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Empathetic talent synthesis, neuro-symbolic allocation tradeoffs & living dossier verification.
            </p>
          </div>
        </div>

        {/* Chat Action Button */}
        <button
          onClick={() => onOpenChat()}
          id="open-advisor-chat-btn"
          className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-md shadow-indigo-600/30 hover:bg-indigo-500 active:scale-95 transition-all self-start sm:self-auto"
        >
          <MessageSquare className="h-4 w-4" />
          <span>Consult Alex on Plan</span>
        </button>
      </div>

      {/* Executive Narrative */}
      <div className="mt-5 rounded-xl bg-white/80 dark:bg-slate-800/60 p-4 border border-indigo-100 dark:border-white/5 shadow-xs">
        <p className="text-xs leading-relaxed text-slate-700 dark:text-slate-200 italic font-sans">
          &ldquo;{advisory.executive_summary}&rdquo;
        </p>

        {/* Quick Suggestion Chips */}
        <div className="mt-3.5 pt-3 border-t border-slate-100 dark:border-white/5 flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-medium text-muted-foreground">Ask Alex:</span>
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onOpenChat(prompt)}
              className="rounded-lg bg-indigo-50 dark:bg-indigo-950/40 px-2.5 py-1 text-[11px] text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 transition-colors border border-indigo-200/60 dark:border-indigo-500/20"
            >
              {prompt} &rarr;
            </button>
          ))}
        </div>
      </div>

      {/* 4 Multi-Dimensional Pillars Grid */}
      <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Pillar 1: Financial Margin */}
        <div className="rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/70 dark:bg-slate-800/40 p-4 backdrop-blur-sm">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-muted-foreground flex items-center gap-1.5 font-medium">
              <TrendingUp className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" /> Commercial Margin
            </span>
            <span className="rounded-md bg-emerald-100 dark:bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-800 dark:text-emerald-300">
              {commercial_health.commercial_rating}
            </span>
          </div>
          <p className="text-xl font-bold font-mono text-slate-900 dark:text-white">
            {commercial_health.gross_margin_pct}%
          </p>
          <div className="mt-2 text-[11px] text-muted-foreground flex justify-between">
            <span>Net Profit:</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400 font-mono">
              {formatCurrency(commercial_health.net_profit)}
            </span>
          </div>
          <div className="text-[10px] text-muted-foreground flex justify-between mt-0.5">
            <span>Revenue:</span>
            <span className="font-mono">{formatCurrency(commercial_health.gross_revenue)}</span>
          </div>
        </div>

        {/* Pillar 2: Burnout Protection */}
        <div className="rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/70 dark:bg-slate-800/40 p-4 backdrop-blur-sm">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-muted-foreground flex items-center gap-1.5 font-medium">
              <Activity className="h-3.5 w-3.5 text-rose-500" /> Burnout Protection
            </span>
            <span className={cn(
              "rounded-md px-2 py-0.5 text-[10px] font-bold",
              people_and_chemistry.fatigue_mitigation_alerts.length > 0
                ? "bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300"
                : "bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300"
            )}>
              {people_and_chemistry.fatigue_mitigation_alerts.length > 0 ? "Guardrails Active" : "Sustainable Pacing"}
            </span>
          </div>
          <p className="text-xl font-bold font-mono text-slate-900 dark:text-white">
            {people_and_chemistry.fatigue_mitigation_alerts.length} <span className="text-xs font-normal text-muted-foreground font-sans">Shielded</span>
          </p>
          {people_and_chemistry.fatigue_mitigation_alerts.length > 0 ? (
            <p className="mt-2 text-[11px] text-slate-700 dark:text-slate-300 leading-snug truncate">
              {people_and_chemistry.fatigue_mitigation_alerts[0].name} ({people_and_chemistry.fatigue_mitigation_alerts[0].fatigue_pct}% stress) capped
            </p>
          ) : (
            <p className="mt-2 text-[11px] text-emerald-600 dark:text-emerald-400">
              Zero overtime pressure flagged across active squads.
            </p>
          )}
        </div>

        {/* Pillar 3: Mentorship Chemistry */}
        <div className="rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/70 dark:bg-slate-800/40 p-4 backdrop-blur-sm">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-muted-foreground flex items-center gap-1.5 font-medium">
              <HeartHandshake className="h-3.5 w-3.5 text-purple-600 dark:text-purple-400" /> Mentorship Pairings
            </span>
            <span className="rounded-md bg-purple-100 dark:bg-purple-500/20 px-2 py-0.5 text-[10px] font-bold text-purple-800 dark:text-purple-300">
              +{people_and_chemistry.mentorship_pairings.length * 250} Synergy
            </span>
          </div>
          <p className="text-xl font-bold font-mono text-slate-900 dark:text-white">
            {people_and_chemistry.mentorship_pairings.length} <span className="text-xs font-normal text-muted-foreground font-sans">Active Pairs</span>
          </p>
          {people_and_chemistry.mentorship_pairings.length > 0 ? (
            <p className="mt-2 text-[11px] text-slate-700 dark:text-slate-300 leading-snug truncate">
              {people_and_chemistry.mentorship_pairings[0].mentee_name} &bull; {people_and_chemistry.mentorship_pairings[0].mentor_name}
            </p>
          ) : (
            <p className="mt-2 text-[11px] text-muted-foreground">Direct staffing without stretch learning.</p>
          )}
        </div>

        {/* Pillar 4: Archetype Chemistry */}
        <div className="rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/70 dark:bg-slate-800/40 p-4 backdrop-blur-sm">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-muted-foreground flex items-center gap-1.5 font-medium">
              <Compass className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400" /> Archetype Chemistry
            </span>
            <span className="rounded-md bg-blue-100 dark:bg-blue-500/20 px-2 py-0.5 text-[10px] font-bold text-blue-800 dark:text-blue-300">
              Balanced
            </span>
          </div>
          <div className="flex items-center gap-1.5 mt-2 flex-wrap">
            {Object.entries(people_and_chemistry.archetype_distribution).map(([arch, count]) => (
              <span
                key={arch}
                className="rounded-md bg-slate-100 dark:bg-slate-700/60 px-2 py-0.5 text-[10px] font-medium text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-white/10"
              >
                {arch}: {count}
              </span>
            ))}
          </div>
          <p className="mt-2 text-[10px] text-muted-foreground">
            Anchored by Pathfinders &amp; Optimizers
          </p>
        </div>
      </div>

      {/* Proactive Recommendations */}
      {strategic_recommendations.length > 0 && (
        <div className="mt-5 space-y-2.5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Proactive Resource Manager Action Items
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {strategic_recommendations.map((rec, i) => (
              <div
                key={i}
                className={cn(
                  "rounded-xl p-3.5 border transition-all text-xs flex flex-col justify-between",
                  rec.severity === "Warning"
                    ? "bg-amber-50/60 border-amber-200 dark:bg-amber-950/20 dark:border-amber-500/30 text-amber-900 dark:text-amber-200"
                    : rec.severity === "Positive"
                    ? "bg-purple-50/60 border-purple-200 dark:bg-purple-950/20 dark:border-purple-500/30 text-purple-900 dark:text-purple-200"
                    : "bg-white/80 border-slate-200 dark:bg-slate-800/40 dark:border-white/10 text-slate-800 dark:text-slate-200"
                )}
              >
                <div>
                  <div className="flex items-center gap-1.5 font-bold mb-1">
                    {rec.severity === "Warning" ? (
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400 shrink-0" />
                    ) : (
                      <Lightbulb className="h-3.5 w-3.5 text-purple-600 dark:text-purple-400 shrink-0" />
                    )}
                    <span>{rec.title}</span>
                  </div>
                  <p className="text-[11px] leading-relaxed opacity-90">{rec.detail}</p>
                </div>
                <div className="mt-2.5 pt-2 border-t border-current/10 flex justify-between items-center text-[10px]">
                  <span className="font-semibold uppercase tracking-wider">{rec.category}</span>
                  <button
                    onClick={() => onOpenChat(`Tell me more about: ${rec.title}`)}
                    className="flex items-center gap-0.5 hover:underline font-medium"
                  >
                    Discuss &rarr;
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
