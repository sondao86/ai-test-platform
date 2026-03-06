"use client";

import * as React from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorBoundaryProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error("ErrorBoundary caught an error:", error, errorInfo);
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null });
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="flex flex-col items-center justify-center min-h-[400px] p-8 text-center bg-red-50/50 rounded-lg border border-red-100 m-4">
                    <div className="bg-red-100 p-3 rounded-full mb-4">
                        <AlertTriangle className="h-8 w-8 text-red-600" />
                    </div>
                    <h2 className="text-xl font-bold text-gray-900 mb-2">Something went wrong</h2>
                    <p className="text-sm text-gray-600 max-w-md mb-6">
                        An unexpected error occurred while rendering this component.
                        {this.state.error?.message && (
                            <span className="block mt-2 font-mono text-xs bg-white p-2 rounded border border-red-200 text-red-700 text-left overflow-auto max-h-32">
                                {this.state.error.message}
                            </span>
                        )}
                    </p>
                    <Button onClick={this.handleReset} variant="outline" className="bg-white hover:bg-gray-50">
                        <RefreshCcw className="h-4 w-4 mr-2" />
                        Try Again
                    </Button>
                </div>
            );
        }

        return this.props.children;
    }
}
