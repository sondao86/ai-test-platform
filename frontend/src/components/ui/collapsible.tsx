"use client";

import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const CollapsibleContext = React.createContext<{
    open: boolean;
    onOpenChange: (open: boolean) => void;
}>({
    open: false,
    onOpenChange: () => { },
});

export function Collapsible({
    open = false,
    onOpenChange,
    children,
    className
}: {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children: React.ReactNode;
    className?: string;
}) {
    const [isOpen, setIsOpen] = React.useState(open);

    React.useEffect(() => {
        setIsOpen(open);
    }, [open]);

    const handleOpenChange = (newOpen: boolean) => {
        setIsOpen(newOpen);
        onOpenChange?.(newOpen);
    };

    return (
        <CollapsibleContext.Provider value={{ open: isOpen, onOpenChange: handleOpenChange }}>
            <div className={cn("w-full", className)}>{children}</div>
        </CollapsibleContext.Provider>
    );
}

export function CollapsibleTrigger({
    children,
    className,
    asChild
}: {
    children: React.ReactNode;
    className?: string;
    asChild?: boolean;
}) {
    const { open, onOpenChange } = React.useContext(CollapsibleContext);

    if (asChild && React.isValidElement(children)) {
        return React.cloneElement(children as React.ReactElement<{ onClick?: React.MouseEventHandler }>, {
            onClick: (e: React.MouseEvent) => {
                const childProps = children.props as { onClick?: React.MouseEventHandler };
                childProps.onClick?.(e);
                onOpenChange(!open);
            }
        });
    }

    return (
        <button
            type="button"
            onClick={() => onOpenChange(!open)}
            className={cn("flex w-full items-center justify-between space-x-4", className)}
        >
            {children}
            <ChevronDown className={cn("h-4 w-4 transition-transform duration-200", open && "rotate-180")} />
        </button>
    );
}

export function CollapsibleContent({
    children,
    className
}: {
    children: React.ReactNode;
    className?: string;
}) {
    const { open } = React.useContext(CollapsibleContext);

    if (!open) return null;

    return (
        <div className={cn("overflow-hidden text-sm transition-all", className)}>
            {children}
        </div>
    );
}
