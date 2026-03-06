"use client";

import Link from "next/link";
import type { TestExecution } from "@/types/api";
import { cn } from "@/lib/utils";

interface Props {
  executions: TestExecution[];
  projectId: string;
}

const STATUS_ICON: Record<string, { icon: string; color: string }> = {
  completed: { icon: "\u2713", color: "text-green-600 bg-green-50" },
  failed: { icon: "!", color: "text-red-600 bg-red-50" },
  running: { icon: "\u25CB", color: "text-blue-600 bg-blue-50" },
  pending: { icon: "\u25CB", color: "text-gray-400 bg-gray-50" },
  cancelled: { icon: "\u2717", color: "text-gray-500 bg-gray-50" },
};

export function ExecutionList({ executions, projectId }: Props) {
  if (executions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No executions yet. Run your test cases to see results.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {executions.map((exec) => {
        const si = STATUS_ICON[exec.status] || STATUS_ICON.pending;
        const passRate =
          exec.total_tests > 0
            ? Math.round((exec.passed / exec.total_tests) * 100)
            : 0;

        return (
          <Link
            key={exec.id}
            href={`/projects/${projectId}/executions/${exec.id}`}
            className="flex items-center gap-4 rounded-lg border bg-white px-4 py-3 hover:border-blue-300 transition-colors"
          >
            <span className={cn("flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold", si.color)}>
              {si.icon}
            </span>

            <div className="flex-1">
              <div className="flex items-center gap-2 text-sm">
                <span className="font-medium text-gray-900 capitalize">{exec.status}</span>
                <span className="text-gray-400">|</span>
                <span className="text-gray-600">
                  {exec.passed}/{exec.total_tests} passed ({passRate}%)
                </span>
              </div>
              <div className="flex gap-3 text-xs text-gray-500 mt-0.5">
                <span>{new Date(exec.created_at).toLocaleString()}</span>
                {exec.duration_ms != null && (
                  <span>{(exec.duration_ms / 1000).toFixed(1)}s</span>
                )}
                <span>by {exec.triggered_by}</span>
              </div>
            </div>

            {/* Mini pass rate bar */}
            <div className="w-24 shrink-0">
              <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                <div
                  className={cn(
                    "h-2 rounded-full",
                    passRate >= 90 ? "bg-green-500" : passRate >= 70 ? "bg-yellow-500" : "bg-red-500"
                  )}
                  style={{ width: `${passRate}%` }}
                />
              </div>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
