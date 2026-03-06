"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { getProjectHistory } from "@/lib/api";
import { HistoryTimeline } from "@/components/workflow/history-timeline";
import { Skeleton } from "@/components/ui/skeleton";

export default function HistoryPage({ params }: { params: Promise<{ id: string }> }) {
    const resolvedParams = React.use(params);
    const projectId = resolvedParams.id;

    const { data: history, isLoading } = useQuery({
        queryKey: ["project-history", projectId],
        queryFn: () => getProjectHistory(projectId),
    });

    if (isLoading) {
        return (
            <div className="space-y-6 max-w-3xl">
                <div>
                    <Skeleton className="h-8 w-64 mb-2" />
                    <Skeleton className="h-4 w-96" />
                </div>
                <div className="space-y-8 mt-8">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="flex gap-4">
                            <Skeleton className="h-10 w-10 rounded-full shrink-0" />
                            <Skeleton className="h-24 w-full rounded-lg" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-3xl">
            <div className="mb-8">
                <h1 className="text-2xl font-bold tracking-tight text-gray-900">Workflow History</h1>
                <p className="text-gray-500 mt-1">
                    Audit log of pipeline executions and phase transitions.
                </p>
            </div>

            <HistoryTimeline history={history || []} />
        </div>
    );
}
