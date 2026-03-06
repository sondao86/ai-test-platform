"use client";

import { type PhaseHistory } from "@/types/api";
import { formatDistanceToNow } from "date-fns";
import {
    CheckCircle2,
    XCircle,
    Clock,
    PlayCircle,
    FileText,
    ListChecks,
    Grid,
    Target
} from "lucide-react";
import { cn } from "@/lib/utils";

interface HistoryTimelineProps {
    history: PhaseHistory[];
}

export function HistoryTimeline({ history }: HistoryTimelineProps) {
    // Sort history newest first
    const sortedHistory = [...history].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );

    if (sortedHistory.length === 0) {
        return (
            <div className="text-center p-8 bg-gray-50 rounded-lg border border-gray-100 border-dashed text-gray-500">
                No history records found for this project yet.
            </div>
        );
    }

    const getPhaseIcon = (phaseId: number) => {
        switch (phaseId) {
            case 1: return FileText;
            case 2: return ListChecks;
            case 3: return Grid;
            case 4: return Target;
            default: return PlayCircle;
        }
    };

    const getStatusConfig = (status: string) => {
        switch (status) {
            case "completed":
                return { icon: CheckCircle2, bg: "bg-green-100", text: "text-green-700", border: "border-green-200" };
            case "error":
                return { icon: XCircle, bg: "bg-red-100", text: "text-red-700", border: "border-red-200" };
            case "running":
                return { icon: PlayCircle, bg: "bg-blue-100", text: "text-blue-700", border: "border-blue-200" };
            default:
                return { icon: Clock, bg: "bg-gray-100", text: "text-gray-700", border: "border-gray-200" };
        }
    };

    return (
        <div className="flow-root">
            <ul role="list" className="-mb-8">
                {sortedHistory.map((event, eventIdx) => {
                    const PhaseIcon = getPhaseIcon(event.phase_id);
                    const statusConfig = getStatusConfig(event.status);
                    const StatusIcon = statusConfig.icon;

                    return (
                        <li key={event.id}>
                            <div className="relative pb-8">
                                {eventIdx !== sortedHistory.length - 1 ? (
                                    <span className="absolute left-5 top-5 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                                ) : null}
                                <div className="relative flex items-start space-x-3 gap-2">
                                    <div className="relative">
                                        <div className={cn(
                                            "flex h-10 w-10 items-center justify-center rounded-full ring-8 ring-white",
                                            statusConfig.bg,
                                            statusConfig.text
                                        )}>
                                            <PhaseIcon className="h-5 w-5" aria-hidden="true" />
                                        </div>
                                    </div>
                                    <div className="min-w-0 flex-1 bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                                        <div className="flex justify-between items-center mb-2">
                                            <div className="flex items-center gap-2">
                                                <span className="font-semibold text-gray-900">
                                                    Phase {event.phase_id}
                                                </span>
                                                <span className={cn(
                                                    "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium border",
                                                    statusConfig.bg,
                                                    statusConfig.text,
                                                    statusConfig.border
                                                )}>
                                                    <StatusIcon className="h-3 w-3" />
                                                    {event.status}
                                                </span>
                                            </div>
                                            <div className="text-xs text-gray-500 whitespace-nowrap">
                                                {formatDistanceToNow(new Date(event.created_at), { addSuffix: true })}
                                            </div>
                                        </div>

                                        {event.error_message && (
                                            <div className="mt-2 text-sm text-red-700 bg-red-50 p-2 rounded border border-red-100 font-mono">
                                                Error: {event.error_message}
                                            </div>
                                        )}

                                        <div className="mt-2 text-xs text-gray-400">
                                            Duration: {event.completed_at
                                                ? `${Math.round((new Date(event.completed_at).getTime() - new Date(event.created_at).getTime()) / 1000)}s`
                                                : 'In progress...'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
}
