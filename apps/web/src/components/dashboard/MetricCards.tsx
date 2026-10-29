"use client";

import React from "react";
import { TrendingUp, Sparkles, Activity, Layers, ArrowUpRight } from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import { Plan } from "@/lib/api";

interface MetricCardsProps {
  plan: Plan;
}

export function MetricCards({ plan }: MetricCardsProps) {
  const breakdown = plan.objective_breakdown || {};
  const profit = breakdown.profit ?? plan.profit_score ?? 412500;
  const growth = breakdown.growth_score ?? plan.growth_score ?? 148000;
  const revenue = breakdown.revenue ?? 795000;
  const laborCost = breakdown.labor_cost ?? 362500;
  const overtimeCost = breakdown.overtime_cost ?? 20000;
  const stretchBonus = breakdown.stretch_bonus ?? 35000;
  const balancePenalty = breakdown.balance_penalty ?? plan.balance_penalty ?? 12300;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Portfolio Profit */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl transition-all hover:border-emerald-500/40 hover:shadow-md">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Portfolio Net Profit</span>
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20">
            <TrendingUp className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white font-mono">
              {formatCurrency(profit)}
            </span>
            <span className="flex items-center text-xs font-semibold text-emerald-600 dark:text-emerald-400">
              <ArrowUpRight className="h-3 w-3" /> +14.2%
            </span>
          </div>
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-muted-foreground border-t border-slate-100 dark:border-white/5 pt-2">
            <span>Rev: {formatCurrency(revenue)}</span>
            <span>Labor: {formatCurrency(laborCost + overtimeCost)}</span>
          </div>
        </div>
      </div>

      {/* 2. Growth & Learning Score */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl transition-all hover:border-purple-500/40 hover:shadow-md">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Team Growth Score</span>
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 ring-1 ring-purple-500/20">
            <Sparkles className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white font-mono">
              {(growth / 1000).toFixed(1)}k <span className="text-sm font-normal text-slate-500 dark:text-slate-400">pts</span>
            </span>
            <span className="rounded bg-purple-500/10 dark:bg-purple-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-purple-700 dark:text-purple-300">
              High Impact
            </span>
          </div>
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-muted-foreground border-t border-slate-100 dark:border-white/5 pt-2">
            <span>Stretch Bonus: +{formatCurrency(stretchBonus)}</span>
            <span>Skill Match: 96%</span>
          </div>
        </div>
      </div>

      {/* 3. Team Billable Utilization */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl transition-all hover:border-indigo-500/40 hover:shadow-md">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Avg Billable Utilization</span>
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 ring-1 ring-indigo-500/20">
            <Activity className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white font-mono">88.4%</span>
            <span className="text-xs text-muted-foreground">Target: 85%</span>
          </div>
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-muted-foreground border-t border-slate-100 dark:border-white/5 pt-2">
            <span>Burnout Penalty: -{formatCurrency(balancePenalty)}</span>
            <span className="text-emerald-600 dark:text-emerald-400 font-medium">Healthy</span>
          </div>
        </div>
      </div>

      {/* 4. Portfolio Projects Selection */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl transition-all hover:border-blue-500/40 hover:shadow-md">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Project Selection Rate</span>
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400 ring-1 ring-blue-500/20">
            <Layers className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white font-mono">3 / 4</span>
            <span className="rounded bg-blue-500/10 dark:bg-blue-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-blue-700 dark:text-blue-300">
              75% Accepted
            </span>
          </div>
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-muted-foreground border-t border-slate-100 dark:border-white/5 pt-2">
            <span>1 Dropped (Low margin)</span>
            <span className="text-slate-500 dark:text-slate-400">100% Mandatory Staffed</span>
          </div>
        </div>
      </div>
    </div>
  );
}
