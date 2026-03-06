import * as React from "react";
import { FileQuestion, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
    icon?: LucideIcon;
    title: string;
    description?: string;
    action?: React.ReactNode;
}

export function EmptyState({
    icon: Icon = FileQuestion,
    title,
    description,
    action,
    className,
    ...props
}: EmptyStateProps) {
    return (
        <div
            className={cn(
                "flex min-h-[400px] flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50/50 p-8 text-center animate-in fade-in-50",
                className
            )}
            {...props}
        >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
                <Icon className="h-6 w-6 text-gray-500" />
            </div>
            <h3 className="mb-2 text-lg font-semibold text-gray-900">{title}</h3>
            {description && (
                <p className="mb-6 max-w-sm text-sm text-gray-500">{description}</p>
            )}
            {action && <div>{action}</div>}
        </div>
    );
}
