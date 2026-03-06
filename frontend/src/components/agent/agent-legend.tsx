import * as React from "react";
import { AGENT_COLORS } from "@/lib/utils";
import { AgentAvatar } from "./agent-avatar";

const AGENT_DESCRIPTIONS: Record<string, string> = {
    business_agent: "Analyzes BRD, extracts requirements (Phase 1 & 2)",
    data_translator_agent: "Maps requirements to test domains (Phase 3)",
    data_engineer_agent: "Builds SQL/dbt assertions (Phase 4)",
    data_governance_agent: "Reviews rules & compliance mappings",
    data_ops_agent: "Reviews test configuration & SLAs",
    data_architect_agent: "Reviews chunks & final specs",
    bi_analytics_agent: "Reviews metric testing coverage",
};

export function AgentLegend() {
    const agents = Object.keys(AGENT_COLORS);

    return (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 overflow-hidden">
            <h4 className="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-3">
                Agent Reference
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                {agents.map((agentId) => (
                    <div key={agentId} className="flex items-start gap-3 p-2 rounded-md hover:bg-gray-50 transition-colors">
                        <AgentAvatar agentId={agentId} size="md" />
                        <div className="flex flex-col">
                            <span className="text-xs font-semibold text-gray-900 capitalize leading-tight">
                                {agentId.replace(/_/g, " ")}
                            </span>
                            <span className="text-[10px] text-gray-500 mt-0.5 leading-snug">
                                {AGENT_DESCRIPTIONS[agentId] || "AI Core Agent"}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
