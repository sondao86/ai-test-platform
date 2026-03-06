import * as React from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AgentAvatar } from "./agent-avatar";

interface ConflictResolverProps {
    description: string;
    agents: string[];
    options: string[];
    onResolve: (selectedOption: string | null, customResolution?: string) => void;
}

export function ConflictResolver({ description, agents, options, onResolve }: ConflictResolverProps) {
    const [customResolution, setCustomResolution] = React.useState("");
    const [selectedOptionIndex, setSelectedOptionIndex] = React.useState<number | null>(null);

    const handleSubmit = () => {
        if (selectedOptionIndex !== null) {
            onResolve(options[selectedOptionIndex]);
        } else if (customResolution.trim()) {
            onResolve(null, customResolution.trim());
        }
    };

    return (
        <div className="border border-orange-200 bg-orange-50 rounded-lg p-4 shadow-sm mb-4">
            <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-orange-600 shrink-0 mt-0.5" />
                <div className="flex-1">
                    <h4 className="text-sm font-semibold text-orange-900 mb-1">Agent Conflict Detected</h4>
                    <p className="text-sm text-orange-800 mb-3">{description}</p>

                    <div className="flex items-center gap-2 mb-4">
                        <span className="text-xs text-orange-700 font-medium">Conflicting Agents:</span>
                        <div className="flex -space-x-2">
                            {agents.map((agent) => (
                                <AgentAvatar
                                    key={agent}
                                    agentId={agent}
                                    size="sm"
                                    className="border-2 border-orange-50"
                                    title={agent}
                                />
                            ))}
                        </div>
                    </div>

                    <div className="space-y-3 mb-4">
                        <span className="text-xs font-semibold text-orange-900 uppercase tracking-wider">Available Options:</span>
                        {options.map((opt, idx) => (
                            <div
                                key={idx}
                                className={`p-3 rounded-md border text-sm cursor-pointer transition-colors ${selectedOptionIndex === idx
                                        ? "border-orange-500 bg-orange-100 text-orange-900 shadow-sm"
                                        : "border-orange-200 bg-white/60 text-orange-800 hover:bg-orange-100 hover:border-orange-300"
                                    }`}
                                onClick={() => {
                                    setSelectedOptionIndex(idx);
                                    setCustomResolution("");
                                }}
                            >
                                <div className="flex items-start gap-2">
                                    <div className={`mt-0.5 h-4 w-4 rounded-full border flex items-center justify-center shrink-0 ${selectedOptionIndex === idx ? "border-orange-600 bg-orange-600" : "border-orange-400"
                                        }`}>
                                        {selectedOptionIndex === idx && <CheckCircle2 className="h-3 w-3 text-white" />}
                                    </div>
                                    <span className="leading-snug">{opt}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-4 pt-4 border-t border-orange-200">
                        <label className="block text-xs font-semibold text-orange-900 uppercase tracking-wider mb-2">
                            Or write a custom resolution:
                        </label>
                        <textarea
                            className="w-full text-sm p-3 rounded-md border border-orange-200 focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white"
                            rows={3}
                            placeholder="Enter your hybrid solution or custom decision here..."
                            value={customResolution}
                            onChange={(e) => {
                                setCustomResolution(e.target.value);
                                setSelectedOptionIndex(null);
                            }}
                        />
                    </div>

                    <div className="mt-4 flex justify-end">
                        <Button
                            onClick={handleSubmit}
                            disabled={selectedOptionIndex === null && !customResolution.trim()}
                            className="bg-orange-600 hover:bg-orange-700 text-white"
                            size="sm"
                        >
                            Resolve Conflict
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
