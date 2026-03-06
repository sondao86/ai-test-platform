"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { getProject, getProjectArtifacts } from "@/lib/api";
import { StatsGrid } from "@/components/dashboard/stats-grid";
import { CategoryChart } from "@/components/dashboard/category-chart";
import { ExportPanel } from "@/components/dashboard/export-panel";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardPage({ params }: { params: Promise<{ id: string }> }) {
    const resolvedParams = React.use(params);
    const projectId = resolvedParams.id;

    const { data: project, isLoading: isProjectLoading } = useQuery({
        queryKey: ["project", projectId],
        queryFn: () => getProject(projectId),
    });

    const { data: artifacts, isLoading: isArtifactsLoading } = useQuery({
        queryKey: ["project-artifacts", projectId],
        queryFn: () => getProjectArtifacts(projectId),
    });

    const isLoading = isProjectLoading || isArtifactsLoading;

    if (isLoading) {
        return (
            <div className="space-y-6">
                <div>
                    <Skeleton className="h-8 w-64 mb-2" />
                    <Skeleton className="h-4 w-96" />
                </div>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24 w-full" />)}
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <Skeleton className="h-64 lg:col-span-2" />
                    <Skeleton className="h-64" />
                </div>
            </div>
        );
    }

    if (!project || !artifacts) return <div className="text-red-500">Failed to load dashboard data.</div>;

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-2xl font-bold tracking-tight text-gray-900">Project Dashboard</h1>
                <p className="text-gray-500 mt-1">
                    Overview of {project.name}.
                </p>
            </div>

            <StatsGrid
                chunkCount={artifacts.chunks.length}
                reqCount={artifacts.requirements.length}
                classCount={artifacts.classifications.length}
                testCaseCount={artifacts.test_cases.length}
            />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    {artifacts.test_cases.length > 0 ? (
                        <CategoryChart testCases={artifacts.test_cases} />
                    ) : (
                        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm h-full flex items-center justify-center text-gray-500">
                            No test cases generated yet. Proceed to Phase 4 to view charts.
                        </div>
                    )}
                </div>
                <div className="lg:col-span-1">
                    <ExportPanel projectId={projectId} testCases={artifacts.test_cases} />
                </div>
            </div>
        </div>
    );
}
