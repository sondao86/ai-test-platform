"use client";

import type { ExecutionSummary } from "@/types/api";

interface Props {
  summary: ExecutionSummary;
  groupBy: "by_category" | "by_severity";
  title: string;
}

const CATEGORY_LABELS: Record<string, string> = {
  completeness: "Completeness",
  consistency: "Consistency",
  timeliness: "Timeliness",
  accuracy: "Accuracy",
  uniqueness: "Uniqueness",
  validity: "Validity",
};

export function CategoryBreakdown({ summary, groupBy, title }: Props) {
  const data = summary[groupBy];
  const entries = Object.entries(data).sort(
    ([, a], [, b]) => b.total - a.total
  );

  if (entries.length === 0) return null;

  return (
    <div className="rounded-lg border bg-white p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">{title}</h3>
      <div className="space-y-3">
        {entries.map(([key, counts]) => {
          return (
            <div key={key}>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="font-medium capitalize">
                  {CATEGORY_LABELS[key] || key}
                </span>
                <span className="text-gray-500">
                  {counts.pass}/{counts.total} passed
                </span>
              </div>
              <div className="flex h-2 rounded-full overflow-hidden bg-gray-100">
                {counts.pass > 0 && (
                  <div
                    className="bg-green-500"
                    style={{ width: `${(counts.pass / counts.total) * 100}%` }}
                  />
                )}
                {counts.fail > 0 && (
                  <div
                    className="bg-red-500"
                    style={{ width: `${(counts.fail / counts.total) * 100}%` }}
                  />
                )}
                {counts.error > 0 && (
                  <div
                    className="bg-orange-500"
                    style={{ width: `${(counts.error / counts.total) * 100}%` }}
                  />
                )}
                {counts.skip > 0 && (
                  <div
                    className="bg-gray-300"
                    style={{ width: `${(counts.skip / counts.total) * 100}%` }}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
