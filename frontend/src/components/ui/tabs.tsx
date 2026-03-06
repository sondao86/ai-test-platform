"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

const TabsContext = React.createContext<{
    value: string;
    onValueChange: (value: string) => void;
}>({
    value: "",
    onValueChange: () => { },
});

export function Tabs({
    defaultValue,
    value,
    onValueChange,
    children,
    className
}: {
    defaultValue?: string;
    value?: string;
    onValueChange?: (value: string) => void;
    children: React.ReactNode;
    className?: string;
}) {
    const [tabValue, setTabValue] = React.useState(value || defaultValue || "");

    React.useEffect(() => {
        if (value !== undefined) {
            setTabValue(value);
        }
    }, [value]);

    const handleValueChange = (newValue: string) => {
        if (value === undefined) {
            setTabValue(newValue);
        }
        onValueChange?.(newValue);
    };

    return (
        <TabsContext.Provider value={{ value: tabValue, onValueChange: handleValueChange }}>
            <div className={cn("w-full", className)}>{children}</div>
        </TabsContext.Provider>
    );
}

export function TabsList({ children, className }: { children: React.ReactNode, className?: string }) {
    return (
        <div className={cn("inline-flex h-9 items-center justify-center rounded-lg bg-gray-100 p-1 text-gray-500", className)}>
            {children}
        </div>
    );
}

export function TabsTrigger({
    value,
    children,
    className
}: {
    value: string;
    children: React.ReactNode;
    className?: string;
}) {
    const context = React.useContext(TabsContext);
    const isSelected = context.value === value;

    return (
        <button
            type="button"
            role="tab"
            aria-selected={isSelected}
            onClick={() => context.onValueChange(value)}
            className={cn(
                "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
                isSelected
                    ? "bg-white text-gray-950 shadow-sm"
                    : "hover:bg-gray-200 hover:text-gray-900",
                className
            )}
        >
            {children}
        </button>
    );
}

export function TabsContent({
    value,
    children,
    className
}: {
    value: string;
    children: React.ReactNode;
    className?: string;
}) {
    const context = React.useContext(TabsContext);

    if (context.value !== value) return null;

    return (
        <div
            role="tabpanel"
            className={cn(
                "mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2",
                className
            )}
        >
            {children}
        </div>
    );
}
