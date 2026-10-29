"use client";

import React from "react";
import {
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Line,
  ComposedChart,
} from "recharts";
import { ParetoPoint } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import { useTheme } from "@/components/theme/ThemeProvider";

interface ParetoChartProps {
  points: ParetoPoint[];
  currentSliderValue: number;
  onSelectPoint?: (point: ParetoPoint) => void;
}

export function ParetoChart({ points, currentSliderValue }: ParetoChartProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  // Format data for chart
  const data = points.map((p) => ({
    ...p,
    profitDisplay: p.profit / 1000,
    growthDisplay: (p.growth_score ?? p.growth ?? 0) / 1000,
    isCurrent: Math.abs(p.slider_value - currentSliderValue) < 0.15,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as ParetoPoint & { isCurrent: boolean };
      return (
        <div className="rounded-xl border border-slate-200 dark:border-white/10 bg-white/95 dark:bg-slate-900/95 p-3.5 shadow-2xl backdrop-blur-xl text-xs">
          <div className="flex items-center justify-between gap-4 border-b border-slate-200 dark:border-white/10 pb-2 mb-2">
            <span className="font-bold text-indigo-600 dark:text-indigo-300">
              Tradeoff Weight: {Math.round(data.slider_value * 100)}% Growth
            </span>
            <span className="rounded bg-emerald-50 dark:bg-emerald-500/20 px-1.5 py-0.5 text-[10px] font-mono font-bold text-emerald-700 dark:text-emerald-300">
              {data.status || "Optimal"}
            </span>
          </div>
          <div className="space-y-1">
            <p className="flex justify-between gap-4 text-slate-700 dark:text-slate-300">
              <span className="text-muted-foreground">Portfolio Profit:</span>
              <span className="font-mono font-semibold text-emerald-600 dark:text-emerald-400">{formatCurrency(data.profit)}</span>
            </p>
            <p className="flex justify-between gap-4 text-slate-700 dark:text-slate-300">
              <span className="text-muted-foreground">Team Growth Score:</span>
              <span className="font-mono font-semibold text-purple-600 dark:text-purple-400">{(((data.growth_score ?? data.growth ?? 0) / 1000).toFixed(1))}k pts</span>
            </p>
            <p className="flex justify-between gap-4 text-slate-700 dark:text-slate-300">
              <span className="text-muted-foreground">Selected Projects:</span>
              <span className="font-mono text-slate-900 dark:text-white">{data.selected_projects_count} / {data.total_projects_count}</span>
            </p>
            <p className="flex justify-between gap-4 text-slate-700 dark:text-slate-300">
              <span className="text-muted-foreground">Stretch Assignments:</span>
              <span className="font-mono text-indigo-600 dark:text-indigo-300">{data.stretch_assignments_count}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? "#334155" : "#e2e8f0"} opacity={0.6} />
          <XAxis
            type="number"
            dataKey="profitDisplay"
            name="Profit"
            unit="k"
            domain={["dataMin - 20", "dataMax + 20"]}
            stroke={isDark ? "#94a3b8" : "#64748b"}
            fontSize={11}
            tickLine={false}
            label={{ value: "Net Profit ($k)", position: "insideBottom", offset: -10, fill: isDark ? "#94a3b8" : "#64748b", fontSize: 11 }}
          />
          <YAxis
            type="number"
            dataKey="growthDisplay"
            name="Growth Score"
            unit="k"
            domain={["dataMin - 10", "dataMax + 10"]}
            stroke={isDark ? "#94a3b8" : "#64748b"}
            fontSize={11}
            tickLine={false}
            label={{ value: "Growth Score (k pts)", angle: -90, position: "insideLeft", offset: 10, fill: isDark ? "#94a3b8" : "#64748b", fontSize: 11 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="growthDisplay"
            stroke="#6366f1"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "#6366f1" }}
            activeDot={{ r: 7, fill: "#a855f7" }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
