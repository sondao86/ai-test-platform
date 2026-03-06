"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { getPipelineStatus } from "@/lib/api";
import { Bot, CheckCircle2, AlertCircle, Clock, Loader2 } from "lucide-react";

interface AgentActivityFeedProps {
    projectId: string;
}

// In a real implementation this would ideally use Server-Sent Events (SSE) or WebSockets.
// For now, we simulate a feed based on polling the current status.
export function AgentActivityFeed({ projectId }: AgentActivityFeedProps) {
    const [logs, setLogs] = React.useState<{ id: string, time: Date, msg: string, type: 'info' | 'success' | 'warning' | 'error' }[]>([]);

    const { data: status } = useQuery({
        queryKey: ["pipeline-status", projectId],
        queryFn: () => getPipelineStatus(projectId),
        refetchInterval: 3000, // Poll every 3 seconds
    });

    // Simple logic to add a log entry if status changes (mocking a real feed)
    React.useEffect(() => {
        if (!status) return;

        const newLog = (msg: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
            setLogs(prev => {
                // Prevent duplicate consecutive logs
                if (prev.length > 0 && prev[0].msg === msg) return prev;
                return [{ id: Math.random().toString(), time: new Date(), msg, type }, ...prev].slice(0, 10);
            });
        };

        if (status.status === "running") {
            const agentMap: Record<number, string> = {
                1: "Business Agent",
                2: "Business Agent",
                3: "Data Translator",
                4: "Data Engineer"
            };
            const currentAgent = agentMap[status.current_phase] || "Core Agent";

            switch (status.current_step) {
                case "primary_generate":
                    newLog(`${currentAgent} generating output for ${status.phase_name}...`, 'info');
                    break;
                case "reviewing":
                    newLog(`Reviewers analyzing ${currentAgent}'s output for ${status.phase_name}...`, 'info');
                    break;
                case "consolidating":
                    newLog(`Consolidator agent merging feedback for ${status.phase_name}...`, 'info');
                    break;
                default: break;
            }
        } else if (status.status === "awaiting_user") {
            newLog(`Phase ${status.current_phase} complete. Awaiting user review.`, 'warning');
        } else if (status.status === "completed") {
            newLog("Pipeline execution completed successfully.", 'success');
        } else if (status.status === "error") {
            newLog("Pipeline execution encountered an error.", 'error');
        }

    }, [status, status?.current_step, status?.status, status?.current_phase, status?.phase_name]);

    const IconMap = {
        info: Loader2,
        success: CheckCircle2,
        warning: Clock,
        error: AlertCircle
    };

    const ColorMap = {
        info: "text-blue-500",
        success: "text-green-500",
        warning: "text-yellow-500",
        error: "text-red-500"
    };

    return (
        <div className="rounded-lg border border-gray-200 bg-white overflow-hidden shadow-sm h-full flex flex-col">
            <div className="bg-gray-50 border-b border-gray-100 p-3 flex items-center gap-2">
                <Bot className="h-4 w-4 text-gray-500" />
                <h3 className="text-sm font-semibold text-gray-700">Live Agent Activity</h3>
                {status?.status === "running" && (
                    <span className="relative flex h-2 w-2 ml-auto">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                    </span>
                )}
            </div>

            <div className="flex-1 p-2 overflow-y-auto max-h-64 flex flex-col-reverse gap-1">
                {logs.map((log, i) => {
                    const Icon = IconMap[log.type];
                    return (
                        <div
                            key={log.id}
                            className={`flex items-start gap-3 p-2 rounded-md text-sm animate-in fade-in slide-in-from-top-2 ${i === 0 ? 'bg-blue-50/50' : 'opacity-80'}`}
                        >
                            <div className="mt-0.5 shrink-0">
                                <Icon className={`h-4 w-4 ${ColorMap[log.type]} ${log.type === 'info' && i === 0 ? 'animate-spin' : ''}`} />
                            </div>
                            <div>
                                <span className="text-gray-900">{log.msg}</span>
                                <div className="text-[10px] text-gray-400 mt-0.5">
                                    {log.time.toLocaleTimeString()}
                                </div>
                            </div>
                        </div>
                    );
                })}
                {logs.length === 0 && (
                    <div className="p-4 text-center text-sm text-gray-400 italic">
                        Waiting for pipeline activity...
                    </div>
                )}
            </div>
        </div>
    );
}
