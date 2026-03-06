import * as React from "react";
import { cn, STATUS_COLORS, SEVERITY_COLORS } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?:
    | "default"
    | "outline"
    | "status"
    | "severity";
    statusValue?: string;
    severityValue?: string;
}

function Badge({
    className,
    variant = "default",
    statusValue,
    severityValue,
    ...props
}: BadgeProps) {
    const baseStyles =
        "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2";

    let styles = "border-transparent bg-gray-900 text-gray-50 hover:bg-gray-900/80";

    if (variant === "outline") {
        styles = "border-gray-200 text-gray-950 hover:bg-gray-100";
    } else if (variant === "status" && statusValue && STATUS_COLORS[statusValue]) {
        styles = `border-transparent ${STATUS_COLORS[statusValue]}`;
    } else if (variant === "severity" && severityValue && SEVERITY_COLORS[severityValue]) {
        styles = SEVERITY_COLORS[severityValue];
    }

    return (
        <div className={cn(baseStyles, styles, className)} {...props} />
    );
}

export { Badge };
