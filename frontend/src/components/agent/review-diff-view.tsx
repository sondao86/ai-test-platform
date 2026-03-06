import * as React from "react";
import { Copy, Check, Info } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ReviewDiffViewProps {
    originalText: string;
    proposedText: string;
}

export function ReviewDiffView({ originalText, proposedText }: ReviewDiffViewProps) {
    const [copied, setCopied] = React.useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(proposedText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!originalText || !proposedText) {
        return (
            <div className="text-sm text-gray-500 italic p-3 bg-gray-50 rounded-md">
                Diff view unavailable. Missing original or proposed text.
            </div>
        );
    }

    return (
        <div className="border border-gray-200 rounded-lg overflow-hidden flex flex-col mt-3">
            <div className="flex bg-gray-50 border-b border-gray-200 text-[10px] font-semibold text-gray-500 uppercase tracking-wider divide-x divide-gray-200">
                <div className="flex-1 py-1.5 px-3">Original</div>
                <div className="flex-1 py-1.5 px-3 flex justify-between items-center">
                    <span>Proposed Change</span>
                    <Button
                        variant="ghost"
                        size="sm"
                        className="h-5 px-1.5 text-gray-500 hover:text-gray-900"
                        onClick={handleCopy}
                        title="Copy Proposed Text"
                    >
                        {copied ? <Check className="h-3 w-3 text-green-600" /> : <Copy className="h-3 w-3" />}
                    </Button>
                </div>
            </div>
            <div className="flex flex-col sm:flex-row divide-y sm:divide-y-0 sm:divide-x divide-gray-200 bg-white">
                <div className="flex-1 p-3">
                    <p className="text-sm font-mono text-red-700 whitespace-pre-wrap break-words bg-red-50/50 p-2 rounded">
                        {originalText}
                    </p>
                </div>
                <div className="flex-1 p-3">
                    <p className="text-sm font-mono text-green-700 whitespace-pre-wrap break-words bg-green-50/50 p-2 rounded">
                        {proposedText}
                    </p>
                </div>
            </div>
            <div className="bg-blue-50/50 p-2 text-xs text-blue-800 flex items-start gap-1.5 border-t border-gray-100">
                <Info className="h-3.5 w-3.5 shrink-0 mt-0.5" />
                <span>Review the proposed changes above. You can accept or reject this suggestion in the main comment card.</span>
            </div>
        </div>
    );
}
