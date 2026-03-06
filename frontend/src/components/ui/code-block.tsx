"use client";

import * as React from "react";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CodeBlockProps extends React.HTMLAttributes<HTMLPreElement> {
    code: string;
    language?: string;
}

export function CodeBlock({ code, language, className, ...props }: CodeBlockProps) {
    const [copied, setCopied] = React.useState(false);

    const onCopy = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative group rounded-md border bg-gray-950 text-gray-50">
            <div className="absolute right-2 top-2 flex items-center space-x-2">
                {language && (
                    <div className="text-xs text-gray-400 font-mono">{language}</div>
                )}
                <button
                    className="rounded-md p-1 text-gray-400 opacity-0 transition-opacity hover:bg-gray-800 hover:text-gray-100 group-hover:opacity-100 focus:opacity-100"
                    onClick={onCopy}
                >
                    {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                </button>
            </div>
            <pre
                className={cn("overflow-x-auto p-4 pt-8 text-sm font-mono leading-relaxed", className)}
                {...props}
            >
                <code>{code}</code>
            </pre>
        </div>
    );
}
