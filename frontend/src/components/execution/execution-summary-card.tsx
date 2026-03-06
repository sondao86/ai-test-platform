"use client";

import type { ExecutionSummary } from "@/types/api";
import { cn } from "@/lib/utils";

interface Props {
  summary: ExecutionSummary;
  className?: string;
}

export function ExecutionSummaryCard({ summary, className }: Props) {
  const stats = [
    { label: "Total", value: summary.total_tests, color: "text-gray-900" },
    { label: "Passed", value: summary.passed, color: "text-green-600" },
    { label: "Failed", value: summary.failed, color: "text-red-600" },
    { label: "Errors", value: summary.errors, color: "text-orange-600" },
    { label: "Skipped", value: summary.skipped, color: "text-gray-400" },
  ];

  const passRate = summary.pass_rate;
  const barColor =
    passRate >= 90 ? "bg-green-500" : passRate >= 70 ? "bg-yellow-500" : "bg-red-500";

  return (
    <div className={cn("rounded-lg border bg-white p-6", className)}>
      {/* Pass rate bar */}
      <div className="mb-4">
        <div className="flex items-end justify-between mb-1">
          <span className="text-sm font-medium text-gray-700">Pass Rate</span>
          <span className={cn("text-2xl font-bold", passRate >= 90 ? "text-green-600" : passRate >= 70 ? "text-yellow-600" : "text-red-600")}>
            {passRate}%
          </span>
        </div>
        <div className="h-3 w-full rounded-full bg-gray-100">
          <div
            className={cn("h-3 rounded-full transition-all duration-500", barColor)}
            style={{ width: `${Math.min(passRate, 100)}%` }}
          />
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-5 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="text-center">
            <p className={cn("text-xl font-bold", s.color)}>{s.value}</p>
            <p className="text-xs text-gray-500">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Duration */}
      {summary.duration_ms != null && (
        <p className="mt-3 text-xs text-gray-500 text-right">
          Duration: {(summary.duration_ms / 1000).toFixed(1)}s
        </p>
      )}
    </div>
  );
}
