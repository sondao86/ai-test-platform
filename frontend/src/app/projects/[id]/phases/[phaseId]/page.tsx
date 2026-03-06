"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { getProjectArtifacts } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { ChunkViewer } from "@/components/phase/artifacts/chunk-viewer";
import { RequirementTable } from "@/components/phase/artifacts/requirement-table";
import { ClassificationMatrix } from "@/components/phase/artifacts/classification-matrix";
import { TestCaseList } from "@/components/phase/artifacts/test-case-list";
import { FileText, ListChecks, Grid, Target } from "lucide-react";

export default function PhaseDetailsPage({
    params
}: {
    params: Promise<{ id: string; phaseId: string }>
}) {
    const resolvedParams = React.use(params);
    const projectId = resolvedParams.id;
    const phaseId = parseInt(resolvedParams.phaseId, 10);

    const { data: artifacts, isLoading, error } = useQuery({
        queryKey: ["project-artifacts", projectId],
        queryFn: () => getProjectArtifacts(projectId),
    });

    if (isLoading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-8 w-64 mb-4" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4 mb-8" />
                <div className="space-y-4">
                    {[1, 2, 3].map(i => <Skeleton key={i} className="h-24 w-full" />)}
                </div>
            </div>
        );
    }

    if (error || !artifacts) {
        return (
            <EmptyState
                icon={FileText}
                title="Error Loading Artifacts"
                description="There was a problem loading the data for this phase. Please try again later."
            />
        );
    }

    const phaseConfig = {
        1: {
            title: "Phase 1: BRD Extraction & Chunking",
            desc: "Review and edit the extracted logical chunks from your Business Requirements Document.",
            data: artifacts.chunks,
            emptyTitle: "No Chunks Found",
            emptyDesc: "No BRD chunks have been generated yet. Please run Phase 1.",
            icon: FileText
        },
        2: {
            title: "Phase 2: Requirement Generation",
            desc: "Review the atomic structured requirements derived from the BRD chunks.",
            data: artifacts.requirements,
            emptyTitle: "No Requirements Found",
            emptyDesc: "No requirements have been generated yet. Please run Phase 2.",
            icon: ListChecks
        },
        3: {
            title: "Phase 3: Test Classification",
            desc: "Map requirements to standard data quality test categories.",
            data: artifacts.classifications,
            emptyTitle: "No Classifications Found",
            emptyDesc: "No classifications have been generated yet. Please run Phase 3.",
            icon: Grid
        },
        4: {
            title: "Phase 4: Test Case Generation",
            desc: "Review the final generated test cases, including SQL and dbt YAML definitions.",
            data: artifacts.test_cases,
            emptyTitle: "No Test Cases Found",
            emptyDesc: "No test cases have been generated yet. Please run Phase 4.",
            icon: Target
        }
    };

    const config = phaseConfig[phaseId as keyof typeof phaseConfig];

    if (!config) {
        return <div className="text-red-500">Invalid phase ID.</div>;
    }

    return (
        <div className="space-y-6">
            <div className="border-b border-gray-200 pb-5">
                <h1 className="text-2xl font-bold tracking-tight text-gray-900">{config.title}</h1>
                <p className="mt-2 text-sm text-gray-500">{config.desc}</p>
            </div>

            {config.data.length === 0 ? (
                <EmptyState
                    icon={config.icon}
                    title={config.emptyTitle}
                    description={config.emptyDesc}
                />
            ) : (
                <div className="mt-6">
                    {phaseId === 1 && <ChunkViewer projectId={projectId} chunks={artifacts.chunks} />}
                    {phaseId === 2 && <RequirementTable projectId={projectId} requirements={artifacts.requirements} />}
                    {phaseId === 3 && <ClassificationMatrix projectId={projectId} classifications={artifacts.classifications} requirements={artifacts.requirements} />}
                    {phaseId === 4 && <TestCaseList projectId={projectId} testCases={artifacts.test_cases} />}
                </div>
            )}
        </div>
    );
}
