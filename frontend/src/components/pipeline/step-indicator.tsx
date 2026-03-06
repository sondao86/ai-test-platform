"use client";

import { cn } from "@/lib/utils";

interface StepIndicatorProps {
    currentStep: string; // primary_generate, reviewing, consolidating, awaiting_user, idle
}

const STEPS = [
    { id: "primary_generate", label: "Generate" },
    { id: "reviewing", label: "Review" },
    { id: "consolidating", label: "Consolidate" },
    { id: "awaiting_user", label: "User Decision" }
];

export function StepIndicator({ currentStep }: StepIndicatorProps) {
    if (currentStep === "idle" || !currentStep) return null;

    const currentIndex = STEPS.findIndex(s => s.id === currentStep);

    return (
        <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-100 overflow-x-auto">
            {STEPS.map((step, index) => {
                const isPast = index < currentIndex;
                const isCurrent = index === currentIndex;

                return (
                    <div key={step.id} className="flex items-center shrink-0">
                        <div
                            className={cn(
                                "px-3 py-1 text-xs font-semibold rounded-full transition-all duration-300",
                                isPast ? "bg-gray-200 text-gray-600" :
                                    isCurrent ? "bg-gray-900 text-white shadow-sm scale-105" :
                                        "bg-white text-gray-400 border border-gray-200"
                            )}
                        >
                            {step.label}
                            {isCurrent && <span className="ml-1 animate-pulse">...</span>}
                        </div>
                        {index < STEPS.length - 1 && (
                            <div className={cn(
                                "w-4 h-[1px] mx-1 transition-colors duration-300",
                                isPast ? "bg-gray-400" : "bg-gray-200"
                            )} />
                        )}
                    </div>
                );
            })}
        </div>
    );
}
