"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { getExecution, cancelExecution } from "@/lib/api";
import { ExecutionSummaryCard } from "@/components/execution/execution-summary-card";
import { CategoryBreakdown } from "@/components/execution/category-breakdown";
import { TestResultRow } from "@/components/execution/test-result-row";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import type { TestResult } from "@/types/api";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  pending: { label: "Pending", color: "bg-gray-100 text-gray-700" },
  running: { label: "Running", color: "bg-blue-100 text-blue-700" },
  completed: { label: "Completed", color: "bg-green-100 text-green-700" },
  failed: { label: "Failed", color: "bg-red-100 text-red-700" },
  cancelled: { label: "Cancelled", color: "bg-yellow-100 text-yellow-700" },
};

export default function ExecutionDetailPage({
  params,
}: {
  params: Promise<{ id: string; executionId: string }>;
}) {
  const { id: projectId, executionId } = React.use(params);
  const queryClient = useQueryClient();
  const [filterResult, setFilterResult] = React.useState<string>("all");
  const [filterCategory, setFilterCategory] = React.useState<string>("all");

  const { data: execution, isLoading } = useQuery({
    queryKey: ["execution", projectId, executionId],
    queryFn: () => getExecution(projectId, executionId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "running" || status === "pending" ? 3000 : false;
    },
  });

  const cancelMutation = useMutation({
    mutationFn: () => cancelExecution(projectId, executionId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["execution", projectId, executionId],
      });
      queryClient.invalidateQueries({
        queryKey: ["executions", projectId],
      });
    },
  });

  const results = execution?.results || [];
  const summary = execution?.summary;

  // Filter results
  const filteredResults = results.filter((r: TestResult) => {
    if (filterResult !== "all" && r.result !== filterResult) return false;
    if (filterCategory !== "all" && r.test_category !== filterCategory)
      return false;
    return true;
  });

  // Get unique categories from results
  const categories = Array.from(
    new Set(results.map((r: TestResult) => r.test_category).filter(Boolean))
  );

  const statusConfig = STATUS_CONFIG[execution?.status || "pending"];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!execution) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center text-red-700">
        Execution not found.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Link
              href={`/projects/${projectId}/executions`}
              className="hover:text-gray-700 hover:underline"
            >
              Executions
            </Link>
            <span>/</span>
            <span className="text-gray-900 font-medium">
              {executionId.slice(0, 8)}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-gray-900">
              Execution Detail
            </h2>
            <Badge className={statusConfig.color}>{statusConfig.label}</Badge>
          </div>
          <p className="text-sm text-gray-500">
            Triggered by {execution.triggered_by || "user"}
            {execution.started_at &&
              ` · Started ${new Date(execution.started_at).toLocaleString()}`}
            {Boolean(execution.config?.dry_run) && (
              <span className="ml-2 inline-flex items-center rounded bg-purple-100 px-1.5 py-0.5 text-xs font-medium text-purple-700">
                DRY RUN
              </span>
            )}
          </p>
        </div>

        {(execution.status === "running" || execution.status === "pending") && (
          <button
            onClick={() => cancelMutation.mutate()}
            disabled={cancelMutation.isPending}
            className="rounded-lg border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50 transition-colors"
          >
            {cancelMutation.isPending ? "Cancelling..." : "Cancel Execution"}
          </button>
        )}
      </div>

      {/* Running indicator */}
      {execution.status === "running" && (
        <div className="flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-700">
          <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          Execution in progress — results will update automatically...
        </div>
      )}

      {/* Summary Card */}
      {summary && <ExecutionSummaryCard summary={summary} />}

      {/* Breakdowns */}
      {summary && (
        <Tabs defaultValue="category">
          <TabsList>
            <TabsTrigger value="category">By Category</TabsTrigger>
            <TabsTrigger value="severity">By Severity</TabsTrigger>
          </TabsList>
          <TabsContent value="category">
            <CategoryBreakdown summary={summary} groupBy="by_category" title="By Category" />
          </TabsContent>
          <TabsContent value="severity">
            <CategoryBreakdown summary={summary} groupBy="by_severity" title="By Severity" />
          </TabsContent>
        </Tabs>
      )}

      {/* Test Results */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Test Results ({filteredResults.length}
            {filteredResults.length !== results.length
              ? ` of ${results.length}`
              : ""}
            )
          </h3>

          <div className="flex items-center gap-2">
            {/* Result filter */}
            <select
              value={filterResult}
              onChange={(e) => setFilterResult(e.target.value)}
              className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="all">All Results</option>
              <option value="pass">Pass</option>
              <option value="fail">Fail</option>
              <option value="error">Error</option>
              <option value="skip">Skip</option>
            </select>

            {/* Category filter */}
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {(cat as string).charAt(0).toUpperCase() +
                    (cat as string).slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {filteredResults.length === 0 ? (
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center text-sm text-gray-500">
            {results.length === 0
              ? execution.status === "running"
                ? "Waiting for results..."
                : "No test results available."
              : "No results match the current filters."}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredResults.map((result: TestResult) => (
              <TestResultRow key={result.id} result={result} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
