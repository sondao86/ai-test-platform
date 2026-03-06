"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listExecutions, startExecution, getTestCases } from "@/lib/api";
import { ExecutionList } from "@/components/execution/execution-list";
import { Skeleton } from "@/components/ui/skeleton";

export default function ExecutionsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: projectId } = React.use(params);
  const queryClient = useQueryClient();
  const [dryRun, setDryRun] = React.useState(false);

  const { data: executions, isLoading } = useQuery({
    queryKey: ["executions", projectId],
    queryFn: () => listExecutions(projectId),
  });

  const { data: testCases } = useQuery({
    queryKey: ["test-cases", projectId],
    queryFn: () => getTestCases(projectId),
  });

  const runMutation = useMutation({
    mutationFn: () =>
      startExecution(projectId, undefined, dryRun ? { dry_run: true } : undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["executions", projectId] });
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Test Executions</h2>
          <p className="text-sm text-gray-500 mt-1">
            Run generated test cases and view results
          </p>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
              className="rounded border-gray-300"
            />
            Dry Run
          </label>

          <button
            onClick={() => runMutation.mutate()}
            disabled={runMutation.isPending || !testCases?.length}
            className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {runMutation.isPending ? (
              <span className="flex items-center gap-2">
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Running...
              </span>
            ) : (
              `Run All Tests${testCases?.length ? ` (${testCases.length})` : ""}`
            )}
          </button>
        </div>
      </div>

      {/* No test cases warning */}
      {testCases && testCases.length === 0 && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
          No test cases generated yet. Complete Phase 4 (Test Case Generation) first.
        </div>
      )}

      {/* Error */}
      {runMutation.isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to start execution: {(runMutation.error as Error).message}
        </div>
      )}

      {/* Executions list */}
      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      ) : (
        <ExecutionList
          executions={executions?.items || []}
          projectId={projectId}
        />
      )}
    </div>
  );
}
