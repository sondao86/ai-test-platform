"use client";

import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface DialogProps {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children: React.ReactNode;
}

const DialogContext = React.createContext<{
    open: boolean;
    onOpenChange: (open: boolean) => void;
}>({
    open: false,
    onOpenChange: () => { },
});

export function Dialog({ open = false, onOpenChange, children }: DialogProps) {
    const [isOpen, setIsOpen] = React.useState(open);

    React.useEffect(() => {
        setIsOpen(open);
    }, [open]);

    const handleOpenChange = (newOpen: boolean) => {
        setIsOpen(newOpen);
        onOpenChange?.(newOpen);
    };

    return (
        <DialogContext.Provider value={{ open: isOpen, onOpenChange: handleOpenChange }}>
            {children}
        </DialogContext.Provider>
    );
}

export function DialogTrigger({ children, asChild = false }: { children: React.ReactElement, asChild?: boolean }) {
    const { onOpenChange } = React.useContext(DialogContext);

    if (asChild && React.isValidElement(children)) {
        return React.cloneElement(children as React.ReactElement<{ onClick?: React.MouseEventHandler }>, {
            onClick: (e: React.MouseEvent) => {
                const childProps = children.props as { onClick?: React.MouseEventHandler };
                childProps.onClick?.(e);
                onOpenChange(true);
            }
        });
    }

    return (
        <div onClick={() => onOpenChange(true)} className="inline-block">
            {children}
        </div>
    );
}

export function DialogContent({ children, className }: { children: React.ReactNode, className?: string }) {
    const { open, onOpenChange } = React.useContext(DialogContext);

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div
                className={cn("relative w-full max-w-lg rounded-xl border bg-white p-6 shadow-lg", className)}
                role="dialog"
            >
                <button
                    onClick={() => onOpenChange(false)}
                    className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-white transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
                >
                    <X className="h-4 w-4" />
                    <span className="sr-only">Close</span>
                </button>
                {children}
            </div>
        </div>
    );
}

export function DialogHeader({ children, className }: { children: React.ReactNode, className?: string }) {
    return (
        <div className={cn("flex flex-col space-y-1.5 text-center sm:text-left", className)}>
            {children}
        </div>
    );
}

export function DialogFooter({ children, className }: { children: React.ReactNode, className?: string }) {
    return (
        <div className={cn("flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 mt-4", className)}>
            {children}
        </div>
    );
}

export function DialogTitle({ children, className }: { children: React.ReactNode, className?: string }) {
    return (
        <h2 className={cn("text-lg font-semibold leading-none tracking-tight", className)}>
            {children}
        </h2>
    );
}

export function DialogDescription({ children, className }: { children: React.ReactNode, className?: string }) {
    return (
        <p className={cn("text-sm text-gray-500", className)}>
            {children}
        </p>
    );
}
