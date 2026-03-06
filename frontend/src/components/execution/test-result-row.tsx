"use client";

import * as React from "react";
import type { TestResult } from "@/types/api";
import { cn } from "@/lib/utils";

interface Props {
  result: TestResult;
}

const RESULT_STYLES: Record<string, { bg: string; text: string; icon: string }> = {
  pass: { bg: "bg-green-50", text: "text-green-700", icon: "\u2713" },
  fail: { bg: "bg-red-50", text: "text-red-700", icon: "\u2717" },
  error: { bg: "bg-orange-50", text: "text-orange-700", icon: "!" },
  skip: { bg: "bg-gray-50", text: "text-gray-500", icon: "\u2014" },
};

export function TestResultRow({ result }: Props) {
  const [expanded, setExpanded] = React.useState(false);
  const style = RESULT_STYLES[result.result || "skip"] || RESULT_STYLES.skip;

  return (
    <div className={cn("rounded-lg border", style.bg)}>
      {/* Summary row */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:opacity-80"
      >
        <span className={cn("flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold", style.text, "bg-white border")}>
          {style.icon}
        </span>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <code className="text-xs font-mono text-gray-500">{result.test_id || "—"}</code>
            <span className="text-sm font-medium text-gray-900 truncate">
              {result.test_title || "Untitled Test"}
            </span>
          </div>
          <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-500">
            {result.test_category && (
              <span className="capitalize">{result.test_category}</span>
            )}
            {result.pipeline_layer && <span>{result.pipeline_layer}</span>}
            <span>{result.executor_type}</span>
            {result.duration_ms != null && <span>{result.duration_ms}ms</span>}
          </div>
        </div>

        <span className={cn("shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase", style.text, "bg-white border")}>
          {result.result || "pending"}
        </span>

        <svg
          className={cn("h-4 w-4 text-gray-400 transition-transform", expanded && "rotate-180")}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded detail */}
      {expanded && (
        <div className="border-t px-4 py-3 space-y-3 bg-white">
          {/* Error message */}
          {result.error_message && (
            <div className="rounded bg-red-50 border border-red-200 px-3 py-2">
              <p className="text-xs font-semibold text-red-700 mb-1">Error</p>
              <p className="text-sm text-red-600 font-mono">{result.error_message}</p>
            </div>
          )}

          {/* SQL executed */}
          {result.sql_executed && (
            <div>
              <p className="text-xs font-semibold text-gray-600 mb-1">SQL Executed</p>
              <pre className="rounded bg-gray-900 text-green-400 text-xs p-3 overflow-x-auto">
                {result.sql_executed}
              </pre>
            </div>
          )}

          {/* Actual vs Expected */}
          <div className="grid grid-cols-2 gap-3">
            {result.actual_output && (
              <div>
                <p className="text-xs font-semibold text-gray-600 mb-1">Actual Output</p>
                <pre className="rounded bg-gray-50 text-xs p-2 overflow-auto max-h-40">
                  {JSON.stringify(result.actual_output, null, 2)}
                </pre>
              </div>
            )}
            {result.expected_output && (
              <div>
                <p className="text-xs font-semibold text-gray-600 mb-1">Expected Output</p>
                <pre className="rounded bg-gray-50 text-xs p-2 overflow-auto max-h-40">
                  {JSON.stringify(result.expected_output, null, 2)}
                </pre>
              </div>
            )}
          </div>

          {/* Rows info */}
          {(result.rows_scanned != null || result.rows_failed != null) && (
            <div className="flex gap-4 text-xs text-gray-600">
              {result.rows_scanned != null && (
                <span>Rows scanned: <strong>{result.rows_scanned}</strong></span>
              )}
              {result.rows_failed != null && (
                <span>Rows failed: <strong className="text-red-600">{result.rows_failed}</strong></span>
              )}
            </div>
          )}

          {/* Logs */}
          {result.logs && result.logs.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-600 mb-1">Execution Logs</p>
              <div className="rounded bg-gray-900 p-2 text-xs font-mono text-gray-300 max-h-32 overflow-auto">
                {result.logs.map((log, i) => (
                  <div key={i}>{log}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
