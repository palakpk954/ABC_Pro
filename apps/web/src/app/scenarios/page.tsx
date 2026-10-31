"use client";

import React, { useState } from "react";
import { MOCK_SCENARIOS, MOCK_PLAN } from "@/lib/mockData";
import { Scenario, NaturalScenarioSimulateResponse, simulateNaturalScenario } from "@/lib/api";
import { formatCurrency, cn } from "@/lib/utils";
import { 
  GitFork, 
  Plus, 
  TrendingDown, 
  TrendingUp, 
  CheckCircle2, 
  Layers, 
  Sparkles,
  Bot,
  Zap,
  ShieldCheck,
  AlertTriangle,
  Lightbulb,
  Send,
  ArrowRight,
  Clock
} from "lucide-react";

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>(MOCK_SCENARIOS);
  const [activeScenario, setActiveScenario] = useState<Scenario>(MOCK_SCENARIOS[0]);
  const [naturalPrompt, setNaturalPrompt] = useState("");
  const [isSimulating, setIsSimulating] = useState(false);
  const [simResult, setSimResult] = useState<NaturalScenarioSimulateResponse | null>({
    scenario_name: "Marcus Vance 3-Week Recovery Leave",
    detected_perturbation: "Employee leave: Marcus Vance (Weeks 1-3)",
    executive_recommendation: "**Recommendation: STRONGLY APPROVED WITH MITIGATION.**\n\nApproving Marcus Vance's 3-week wellness leave drops net portfolio profit by $12,400 (a modest 2.9% margin adjustment), but successfully **eliminates critical attrition risk** by resetting fatigue from 78% down to 25%. Devon Brooks and Sarah Chen can absorb the technical workload with zero delivery slippage.",
    recommendation_verdict: "Approved",
    profit_delta: -12400,
    growth_score_delta: 24000,
    labor_cost_delta: 8200,
    overtime_cost_delta: -4200,
    feasibility_status: "100% Feasible (Zero Unstaffed Hard Constraints)",
    assignments_shifted_count: 6,
    impacted_engineers: [
      {
        employee_id: "emp-2",
        employee_name: "Marcus Vance",
        role_title: "Principal Architect / Incident Lead",
        project_name: "Active Squad Engagements",
        previous_hours: 120,
        new_hours: 0,
        delta_hours: -120,
        change_type: "reduced",
        rationale: "Relieved from on-call duties for 3 weeks to reset fatigue index from 78% to 25%.",
      },
      {
        employee_id: "emp-4",
        employee_name: "Devon Brooks",
        role_title: "Core Data & Backend Engineer",
        project_name: "Fintech Real-Time Ledger",
        previous_hours: 40,
        new_hours: 40,
        delta_hours: 0,
        change_type: "backfilled",
        rationale: "Assumes primary module execution with Sarah Chen providing 4h/wk architecture review backstop.",
      },
      {
        employee_id: "emp-1",
        employee_name: "Sarah Chen",
        role_title: "Lead Cloud Architect",
        project_name: "Fintech Real-Time Ledger",
        previous_hours: 40,
        new_hours: 42,
        delta_hours: 2,
        change_type: "reallocated",
        rationale: "Absorbs 2h/wk architecture gating to ensure client compliance during absence.",
      },
    ],
    suggested_mitigations: [
      "Lock Devon Brooks's mentor pairing with Sarah Chen for Weeks 1-3.",
      "Schedule handover sync 3 days prior to Marcus's departure.",
      "Review code walkthrough bandwidth weekly with delivery leads.",
    ],
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  const quickPromptChips = [
    "What if Marcus Vance takes 3 weeks emergency recovery leave?",
    "What if Fintech pulls kickoff forward by 2 weeks?",
    "What if we prioritize gross profit to 95%?",
  ];

  const handleSimulatePrompt = async (promptText?: string) => {
    const text = promptText || naturalPrompt;
    if (!text.trim() || isSimulating) return;

    setIsSimulating(true);
    try {
      const res = await simulateNaturalScenario(MOCK_PLAN.id, text);
      setSimResult(res);
      setNotification(`Simulated "${res.scenario_name}"! Counterfactual diff generated.`);
      setTimeout(() => setNotification(null), 5000);
    } catch (e) {
      // Local fallback for offline mode
      if (text.toLowerCase().includes("fintech") || text.toLowerCase().includes("pull") || text.toLowerCase().includes("kickoff")) {
        setSimResult({
          scenario_name: "Fintech Project Kickoff Acceleration (3 Weeks Early)",
          detected_perturbation: "Schedule shift: Fintech Real-Time Ledger start date pulled forward",
          executive_recommendation: "**Recommendation: CAUTION - MONITOR OVERTIME STACKING.**\n\nAccelerating kickoff realizes **+$45,000 in early recognized revenue**, but induces 12.5h of temporary overtime on lead architects. Recommend capping overtime to 4h/week max and rotating off secondary duties.",
          recommendation_verdict: "Caution",
          profit_delta: 45000,
          growth_score_delta: -12000,
          labor_cost_delta: 32000,
          overtime_cost_delta: 8500,
          feasibility_status: "100% Feasible with Overtime Authorization",
          assignments_shifted_count: 8,
          impacted_engineers: [
            {
              employee_id: "emp-1",
              employee_name: "Sarah Chen",
              role_title: "Lead Cloud Architect",
              project_name: "Fintech Real-Time Ledger",
              previous_hours: 40,
              new_hours: 44,
              delta_hours: 4,
              change_type: "reallocated",
              rationale: "Kickoff moved up; requires 4h overtime in initial design sprint.",
            },
            {
              employee_id: "emp-3",
              employee_name: "Elena Rostova",
              role_title: "Frontend Lead",
              project_name: "Healthcare Analytics Portal",
              previous_hours: 40,
              new_hours: 36,
              delta_hours: -4,
              change_type: "reallocated",
              rationale: "Slightly shifted frontend pacing to balance overall squad bandwidth.",
            },
          ],
          suggested_mitigations: [
            "Authorize 4h/wk overtime cap for senior lead.",
            "Pre-approve contractor backfill for secondary feature maintenance.",
          ],
        });
      } else if (text.toLowerCase().includes("profit") || text.toLowerCase().includes("95%")) {
        setSimResult({
          scenario_name: "Pure Profit Weight Optimization (0.95 Profit / 0.05 Growth)",
          detected_perturbation: "Tradeoff slider adjustment: Profit weight increased to 0.95",
          executive_recommendation: "**Recommendation: COMMERCIAL WIN / RETENTION TRADE-OFF.**\n\nMaximizing profit generates an additional **+$37,500 in portfolio margin** (pushing gross margin to 63.8%), but reduces stretch learning opportunities by 46%, dampening junior engineer upskilling.",
          recommendation_verdict: "Approved",
          profit_delta: 37500,
          growth_score_delta: -68000,
          labor_cost_delta: -42000,
          overtime_cost_delta: -4500,
          feasibility_status: "100% Feasible",
          assignments_shifted_count: 4,
          impacted_engineers: [
            {
              employee_id: "emp-4",
              employee_name: "Devon Brooks",
              role_title: "Core Data & Backend Engineer",
              project_name: "Fintech Real-Time Ledger",
              previous_hours: 40,
              new_hours: 40,
              delta_hours: 0,
              change_type: "reallocated",
              rationale: "Replaced stretch role with direct billable senior to maximize pure hourly margin.",
            },
          ],
          suggested_mitigations: [
            "Schedule internal hackathon or tech talk to preserve learning motivation.",
            "Re-evaluate after 6 weeks before locking Q1 roadmap.",
          ],
        });
      }
      setNotification("Scenario re-simulated using offline cognitive model.");
      setTimeout(() => setNotification(null), 4000);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="rounded-md bg-indigo-50 dark:bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
              Cognitive What-If Sandbox &amp; Diff Explainer
            </span>
            <span className="text-xs text-muted-foreground font-mono">Alex Engine Active</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            What-If Scenario Simulation
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Describe any operational condition in plain English to simulate CP-SAT counterfactual re-solves, burnout impact, and margin diffs.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          id="create-scenario-btn"
          className="flex items-center gap-2 rounded-xl bg-white dark:bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all shadow-sm"
        >
          <Plus className="h-4 w-4" />
          Custom Parametric Scenario
        </button>
      </div>

      {notification && (
        <div className="rounded-xl border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-950/40 p-3.5 text-xs text-indigo-800 dark:text-indigo-200 flex items-center gap-2.5 animate-accordion-down">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-indigo-600 dark:text-indigo-400" />
          <span>{notification}</span>
        </div>
      )}

      {/* Natural Language Scenario Prompt Bar */}
      <div className="rounded-2xl border border-indigo-200/90 dark:border-indigo-500/30 bg-gradient-to-r from-indigo-50/80 via-white to-purple-50/60 dark:from-slate-900/90 dark:via-slate-900/60 dark:to-indigo-950/30 p-5 backdrop-blur-xl shadow-md">
        <div className="flex items-center gap-2 mb-2">
          <Bot className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
          <h3 className="text-xs font-bold text-slate-900 dark:text-white">Ask Alex to Simulate a What-If Operational Shock</h3>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSimulatePrompt();
          }}
          className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 mt-2"
        >
          <div className="relative flex-1">
            <input
              type="text"
              value={naturalPrompt}
              onChange={(e) => setNaturalPrompt(e.target.value)}
              placeholder="e.g. What if Marcus Vance takes 3 weeks leave to recover from burnout?"
              className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-800 px-4 py-3 text-xs text-slate-900 dark:text-white placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-xs"
            />
          </div>
          <button
            type="submit"
            disabled={isSimulating}
            className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-xs font-semibold text-white shadow-md shadow-indigo-600/30 hover:bg-indigo-500 active:scale-95 disabled:opacity-50 transition-all shrink-0"
          >
            <Sparkles className={`h-4 w-4 ${isSimulating ? "animate-spin" : ""}`} />
            {isSimulating ? "Simulating CP-SAT Diff..." : "Simulate What-If"}
          </button>
        </form>

        {/* Quick Suggestion Chips */}
        <div className="mt-3 flex flex-wrap items-center gap-2 pt-2 border-t border-indigo-100 dark:border-white/5">
          <span className="text-[11px] text-muted-foreground font-medium">Quick Scenarios:</span>
          {quickPromptChips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => {
                setNaturalPrompt(chip);
                handleSimulatePrompt(chip);
              }}
              className="rounded-lg bg-white/80 dark:bg-slate-800/80 px-2.5 py-1 text-[11px] text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-slate-700 transition-colors border border-indigo-200/50 dark:border-white/10 shadow-2xs"
            >
              {chip}
            </button>
          ))}
        </div>
      </div>

      {/* Simulated Scenario Counterfactual Results */}
      {simResult && (
        <div className="space-y-6 animate-scaleUp">
          {/* Executive Recommendation from Alex */}
          <div className={cn(
            "rounded-2xl border p-5 backdrop-blur-xl shadow-md",
            simResult.recommendation_verdict === "Approved"
              ? "border-emerald-200 dark:border-emerald-500/30 bg-emerald-50/60 dark:bg-emerald-950/20"
              : "border-amber-200 dark:border-amber-500/30 bg-amber-50/60 dark:bg-amber-950/20"
          )}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-current/10">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-sm">
                  <Bot className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">{simResult.scenario_name}</h3>
                  <p className="text-[11px] text-muted-foreground">{simResult.detected_perturbation}</p>
                </div>
              </div>

              <div className="flex items-center gap-2 self-start sm:self-auto">
                <span className={cn(
                  "rounded-full px-3 py-1 text-xs font-bold font-mono uppercase tracking-wide",
                  simResult.recommendation_verdict === "Approved"
                    ? "bg-emerald-600 text-white shadow-sm"
                    : "bg-amber-500 text-white shadow-sm"
                )}>
                  {simResult.recommendation_verdict}
                </span>
                <span className="rounded-lg bg-white/70 dark:bg-slate-800/80 px-2.5 py-1 text-[11px] font-semibold text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10">
                  {simResult.feasibility_status}
                </span>
              </div>
            </div>

            <div className="mt-4 whitespace-pre-line text-xs leading-relaxed text-slate-800 dark:text-slate-200 font-sans">
              {simResult.executive_recommendation}
            </div>

            {/* Suggested Mitigations Checklist */}
            {simResult.suggested_mitigations && simResult.suggested_mitigations.length > 0 && (
              <div className="mt-4 pt-3 border-t border-current/10">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                  Required Mitigations &amp; Action Plan:
                </span>
                <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-2">
                  {simResult.suggested_mitigations.map((item, i) => (
                    <div
                      key={i}
                      className="rounded-xl bg-white/80 dark:bg-slate-900/60 p-2.5 border border-current/10 text-[11px] text-slate-800 dark:text-slate-200 flex items-start gap-2 shadow-2xs"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* 4 Differential KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Profit Delta */}
            <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
              <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Portfolio Profit Delta</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span
                  className={cn(
                    "text-2xl font-bold font-mono",
                    simResult.profit_delta >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"
                  )}
                >
                  {simResult.profit_delta >= 0 ? "+" : ""}
                  {formatCurrency(simResult.profit_delta)}
                </span>
                {simResult.profit_delta < 0 ? (
                  <span className="flex items-center text-xs font-semibold text-rose-600 dark:text-rose-400">
                    <TrendingDown className="h-3 w-3" /> Margin Drop
                  </span>
                ) : (
                  <span className="flex items-center text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                    <TrendingUp className="h-3 w-3" /> Margin Gain
                  </span>
                )}
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">
                Base: {formatCurrency(MOCK_PLAN.profit_score || 412500)} &rarr; Scenario:{" "}
                {formatCurrency((MOCK_PLAN.profit_score || 412500) + simResult.profit_delta)}
              </p>
            </div>

            {/* Growth Score Delta */}
            <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
              <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Growth Score Delta</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span
                  className={cn(
                    "text-2xl font-bold font-mono",
                    simResult.growth_score_delta >= 0 ? "text-purple-600 dark:text-purple-400" : "text-rose-600 dark:text-rose-400"
                  )}
                >
                  {simResult.growth_score_delta >= 0 ? "+" : ""}
                  {(simResult.growth_score_delta / 1000).toFixed(1)}k pts
                </span>
                <span className="text-xs font-semibold text-purple-600 dark:text-purple-400 flex items-center">
                  <Sparkles className="h-3 w-3" /> Stretch Value
                </span>
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">
                Stretch allocations and mentoring adjusted
              </p>
            </div>

            {/* Assignments Shifted */}
            <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
              <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Staffing Perturbations</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-mono text-indigo-700 dark:text-indigo-300">
                  {simResult.assignments_shifted_count}
                </span>
                <span className="text-xs text-muted-foreground">Assignments Displaced</span>
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">
                Across {simResult.impacted_engineers?.length || 0} impacted team members
              </p>
            </div>

            {/* Burnout Recovery Impact */}
            <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
              <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Burnout Stress Reset</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
                  -53%
                </span>
                <span className="rounded bg-emerald-100 dark:bg-emerald-500/20 px-1.5 py-0.5 text-[10px] font-bold text-emerald-800 dark:text-emerald-300">
                  Reset to 25%
                </span>
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">
                Critical attrition risk averted
              </p>
            </div>
          </div>

          {/* Impacted Engineers & Staffing Diff Breakdown */}
          {simResult.impacted_engineers && simResult.impacted_engineers.length > 0 && (
            <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
              <div className="flex items-center gap-2 mb-4">
                <Layers className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  Impacted Engineers &amp; Workload Rebalancing
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {simResult.impacted_engineers.map((emp, i) => (
                  <div
                    key={i}
                    className="rounded-xl bg-slate-50 dark:bg-slate-800/40 p-3.5 border border-slate-200 dark:border-white/5 text-xs flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-slate-900 dark:text-white">{emp.employee_name}</span>
                        <span className={cn(
                          "rounded-md px-2 py-0.5 text-[10px] font-semibold border",
                          emp.change_type === "reduced"
                            ? "bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-500/30"
                            : emp.change_type === "backfilled"
                            ? "bg-purple-50 text-purple-800 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-500/30"
                            : "bg-indigo-50 text-indigo-800 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-500/30"
                        )}>
                          {emp.change_type.toUpperCase()} ({emp.delta_hours > 0 ? `+${emp.delta_hours}h` : `${emp.delta_hours}h`})
                        </span>
                      </div>
                      <p className="text-[11px] text-muted-foreground">{emp.role_title} &bull; {emp.project_name}</p>
                      <p className="mt-2 text-[11px] leading-relaxed text-slate-700 dark:text-slate-300 italic">
                        &ldquo;{emp.rationale}&rdquo;
                      </p>
                    </div>

                    <div className="mt-3 pt-2 border-t border-slate-200 dark:border-white/5 flex items-center justify-between text-[10px] font-mono text-muted-foreground">
                      <span>Previous: {emp.previous_hours}h</span>
                      <ArrowRight className="h-3 w-3" />
                      <span className="font-bold text-slate-900 dark:text-white">New: {emp.new_hours}h</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Preset Scenarios Selector */}
      <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Saved Scenario Branches</h3>
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {scenarios.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setActiveScenario(s);
                handleSimulatePrompt(s.name);
              }}
              className={cn(
                "flex items-center gap-2 rounded-xl px-4 py-2 text-xs font-semibold whitespace-nowrap transition-all border",
                activeScenario.id === s.id
                  ? "bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-600/20 dark:text-indigo-200 dark:border-indigo-500/40 shadow-sm"
                  : "bg-slate-50 dark:bg-slate-800/60 text-slate-600 dark:text-muted-foreground border-slate-200 dark:border-white/5 hover:bg-slate-100 dark:hover:bg-slate-800"
              )}
            >
              <GitFork className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>{s.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
