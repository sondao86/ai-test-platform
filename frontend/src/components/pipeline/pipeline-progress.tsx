"use client";

import { cn } from "@/lib/utils";
import { PlayCircle, CheckCircle2, Clock, AlertCircle } from "lucide-react";

interface PipelineProgressProps {
    currentPhase: number;
    currentStep?: string;
    status: string; // running, awaiting_user, completed, error, created
    className?: string;
}

const PHASES = [
    { id: 1, name: "Ingest & Chunk" },
    { id: 2, name: "Requirements" },
    { id: 3, name: "Classification" },
    { id: 4, name: "Test Cases" }
];

export function PipelineProgress({ currentPhase, currentStep, status, className }: PipelineProgressProps) {
    // Calculate raw progress %
    let progress = 0;
    if (currentPhase > 0) {
        progress = ((currentPhase - 1) / 4) * 100;
    }
    if (status === "completed") {
        progress = 100;
    }

    const stepLabels: Record<string, string> = {
        primary_generate: "Generating Content",
        reviewing: "Agent Review",
        consolidating: "Consolidating Feedback",
        awaiting_user: "Awaiting User Review",
        idle: "Idle"
    };

    return (
        <div className={cn("w-full bg-white rounded-lg border border-gray-200 p-6 shadow-sm", className)}>
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h3 className="text-lg font-semibold text-gray-900">Pipeline Progress</h3>
                    <p className="text-sm text-gray-500 mt-1 capitalize flex items-center gap-1.5">
                        {status === "running" && <PlayCircle className="h-4 w-4 text-blue-500 animate-pulse" />}
                        {status === "awaiting_user" && <Clock className="h-4 w-4 text-yellow-500" />}
                        {status === "completed" && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                        {status === "error" && <AlertCircle className="h-4 w-4 text-red-500" />}
                        {status === "completed" ? "Completed" : (stepLabels[currentStep || "idle"] || status.replace(/_/g, " "))}
                    </p>
                </div>
                <div className="text-3xl font-bold tracking-tight text-gray-300">
                    {Math.round(progress)}%
                </div>
            </div>

            <div className="relative">
                <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-100 -translate-y-1/2 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-blue-600 transition-all duration-700 ease-in-out"
                        style={{ width: `${progress}%` }}
                    />
                </div>

                <div className="relative flex justify-between">
                    {PHASES.map((phase) => {
                        const isCompleted = status === "completed" || phase.id < currentPhase;
                        const isCurrent = phase.id === currentPhase && status !== "completed";

                        return (
                            <div key={phase.id} className="flex flex-col items-center">
                                <div
                                    className={cn(
                                        "w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold border-2 bg-white transition-colors duration-300 z-10",
                                        isCompleted ? "border-blue-600 text-blue-600" :
                                            isCurrent ? "border-blue-500 text-blue-500 ring-4 ring-blue-50" :
                                                "border-gray-200 text-gray-400"
                                    )}
                                >
                                    {isCompleted ? <CheckCircle2 className="h-5 w-5" /> : phase.id}
                                </div>
                                <div className={cn(
                                    "mt-3 text-xs font-medium text-center whitespace-nowrap",
                                    (isCompleted || isCurrent) ? "text-gray-900" : "text-gray-500"
                                )}>
                                    {phase.name}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
