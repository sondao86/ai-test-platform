"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { getProject, getPipelineStatus } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { PipelineProgress } from "@/components/pipeline/pipeline-progress";
import { StepIndicator } from "@/components/pipeline/step-indicator";
import { AgentActivityFeed } from "@/components/pipeline/agent-activity-feed";

export default function ProjectOverviewPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const resolvedParams = React.use(params);
  const projectId = resolvedParams.id;

  const { data: project, isLoading: isProjectLoading, error: projectError } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => getProject(projectId),
  });

  const { data: status } = useQuery({
    queryKey: ["pipeline-status", projectId],
    queryFn: () => getPipelineStatus(projectId),
    refetchInterval: project?.status === "running" ? 3000 : false,
    enabled: !!project,
  });

  if (isProjectLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64 mb-4" />
        <Skeleton className="h-4 w-full max-w-2xl mb-8" />
        <Skeleton className="h-48 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="text-center p-8 bg-red-50 text-red-600 rounded-lg border border-red-200">
        Failed to load project details or project not found.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">{project.name}</h1>
        <p className="mt-2 text-sm text-gray-500 whitespace-pre-wrap">{project.description}</p>
      </div>

      <PipelineProgress
        currentPhase={project.current_phase || 0}
        currentStep={status?.current_step}
        status={project.status}
      />

      {project.status === "running" && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Current Execution Step</h3>
          <StepIndicator currentStep={status?.current_step || "idle"} />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-4">Project Details</h3>
          <dl className="space-y-4 text-sm">
            <div className="grid grid-cols-3 gap-4">
              <dt className="text-gray-500 font-medium">Created at</dt>
              <dd className="col-span-2 text-gray-900">{new Date(project.created_at).toLocaleString()}</dd>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <dt className="text-gray-500 font-medium">Last Updated</dt>
              <dd className="col-span-2 text-gray-900">{new Date(project.updated_at).toLocaleString()}</dd>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <dt className="text-gray-500 font-medium">Status</dt>
              <dd className="col-span-2 capitalize text-gray-900">{project.status.replace('_', ' ')}</dd>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <dt className="text-gray-500 font-medium">Phase</dt>
              <dd className="col-span-2 text-gray-900">Phase {project.current_phase}</dd>
            </div>
          </dl>
        </div>

        <div className="h-[300px]">
          <AgentActivityFeed projectId={projectId} />
        </div>
      </div>
    </div>
  );
}
