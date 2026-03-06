import * as React from "react";
import { AGENT_COLORS } from "@/lib/utils";
import { Bot, UserSearch, Network, Database, ShieldAlert, Cpu, LineChart } from "lucide-react";
import { cn } from "@/lib/utils";

interface AgentAvatarProps {
    agentId: string;
    className?: string;
    size?: "sm" | "md" | "lg";
    title?: string;
}

const AGENT_ICONS: Record<string, React.ElementType> = {
    business_agent: UserSearch,
    data_translator_agent: Network,
    data_engineer_agent: Database,
    data_governance_agent: ShieldAlert,
    data_ops_agent: Cpu,
    data_architect_agent: Bot, // Fallback to Bot since architecture isn't a direct lucide icon easily recognizable, or use a custom one
    bi_analytics_agent: LineChart,
};

export function AgentAvatar({ agentId, className, size = "md", title }: AgentAvatarProps) {
    const Icon = AGENT_ICONS[agentId] || Bot;
    const colorClass = AGENT_COLORS[agentId] || "bg-gray-100 text-gray-800";

    const sizeClasses = {
        sm: "h-6 w-6 rounded-md",
        md: "h-8 w-8 rounded-full",
        lg: "h-10 w-10 rounded-full",
    };

    const iconSizes = {
        sm: "h-3 w-3",
        md: "h-4 w-4",
        lg: "h-5 w-5",
    };

    return (
        <div
            className={cn(
                "flex items-center justify-center flex-shrink-0",
                sizeClasses[size],
                colorClass,
                className
            )}
            title={title || agentId.replace(/_/g, " ")}
        >
            <Icon className={iconSizes[size]} />
        </div>
    );
}
