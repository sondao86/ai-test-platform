"use client";

import * as React from "react";
import type { AgentReview } from "@/types/api";
import { AGENT_COLORS } from "@/lib/utils";
import { CheckCircle2, AlertCircle, Info } from "lucide-react";
import { AgentAvatar } from "./agent-avatar";

interface Props {
    reviews: AgentReview[];
    onAgentClick?: (agentId: string) => void;
}

export function ReviewSummaryBar({ reviews, onAgentClick }: Props) {
    if (!reviews || reviews.length === 0) return null;

    const approved = reviews.filter(r => r.status === "approved").length;
    const changes = reviews.filter(r => r.status === "changes_requested").length;
    const additions = reviews.filter(r => r.status === "additions_suggested").length;

    return (
        <div className="flex flex-col sm:flex-row items-center justify-between bg-white border border-gray-200 rounded-lg p-3 shadow-sm gap-4">
            <div className="flex items-center gap-4 text-sm font-medium shrink-0">
                <span className="text-gray-900">Review Summary:</span>
                <div className="flex gap-3">
                    {approved > 0 && <span className="flex items-center text-green-700 gap-1"><CheckCircle2 className="h-4 w-4" /> {approved} Approved</span>}
                    {changes > 0 && <span className="flex items-center text-yellow-700 gap-1"><AlertCircle className="h-4 w-4" /> {changes} Changes</span>}
                    {additions > 0 && <span className="flex items-center text-blue-700 gap-1"><Info className="h-4 w-4" /> {additions} Additions</span>}
                </div>
            </div>

            <div className="flex flex-wrap items-center justify-end gap-2 flex-1">
                {reviews.map(review => {
                    const colorClass = AGENT_COLORS[review.agent_id] || "bg-gray-100 text-gray-800";
                    let Icon = Info;
                    if (review.status === "approved") Icon = CheckCircle2;
                    if (review.status === "changes_requested") Icon = AlertCircle;

                    return (
                        <button
                            key={review.id}
                            onClick={() => onAgentClick?.(review.agent_id)}
                            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide uppercase transition-transform hover:scale-105 ${colorClass}`}
                            title={`${review.agent_name}: ${review.status.replace(/_/g, " ")}`}
                        >
                            <AgentAvatar agentId={review.agent_id} size="sm" className={colorClass} />
                            <span>{review.agent_name.split(' ')[0]}</span>
                            <Icon className="h-3 w-3 ml-0.5 opacity-80" />
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
