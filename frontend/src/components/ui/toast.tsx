"use client";

import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export type ToastType = "success" | "error" | "info";

export interface Toast {
    id: string;
    title: string;
    description?: string;
    type?: ToastType;
}

interface ToastContextType {
    toasts: Toast[];
    toast: (options: Omit<Toast, "id">) => void;
    dismiss: (id: string) => void;
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
    const [toasts, setToasts] = React.useState<Toast[]>([]);

    const toast = React.useCallback(({ title, description, type = "info" }: Omit<Toast, "id">) => {
        const id = Math.random().toString(36).substring(2, 9);
        setToasts((prev) => [...prev, { id, title, description, type }]);

        // Auto dismiss after 3 seconds
        setTimeout(() => {
            setToasts((prev) => prev.filter((t) => t.id !== id));
        }, 3000);
    }, []);

    const dismiss = React.useCallback((id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    return (
        <ToastContext.Provider value={{ toasts, toast, dismiss }}>
            {children}
            <div className="fixed bottom-0 right-0 z-50 m-6 flex flex-col gap-2">
                {toasts.map((t) => (
                    <div
                        key={t.id}
                        className={cn(
                            "pointer-events-auto flex w-full max-w-sm items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all",
                            t.type === "error" && "border-red-200 bg-red-50 text-red-900",
                            t.type === "success" && "border-green-200 bg-green-50 text-green-900",
                            t.type === "info" && "bg-white text-gray-950"
                        )}
                    >
                        <div>
                            <div className="text-sm font-semibold">{t.title}</div>
                            {t.description && <div className="text-sm opacity-90">{t.description}</div>}
                        </div>
                        <button
                            onClick={() => dismiss(t.id)}
                            className="absolute right-2 top-2 rounded-md p-1 opacity-70 transition-opacity hover:opacity-100"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}

export function useToast() {
    const context = React.useContext(ToastContext);
    if (!context) {
        throw new Error("useToast must be used within a ToastProvider");
    }
    return context;
}
