"use client";

import * as React from "react";
import { type TestCategoryMap, type Requirement } from "@/types/api";
import { ClassificationEditor } from "./classification-editor";
import { Dialog, DialogContent } from "@/components/ui/dialog";

interface ClassificationMatrixProps {
    projectId: string;
    classifications: TestCategoryMap[];
    requirements: Requirement[];
}

const CATEGORIES = [
    "completeness",
    "consistency",
    "timeliness",
    "accuracy",
    "uniqueness",
    "validity"
];

function getIntensityClass(confidence: number) {
    if (confidence >= 0.9) return "bg-blue-600 text-white";
    if (confidence >= 0.7) return "bg-blue-400 text-white";
    if (confidence >= 0.5) return "bg-blue-200 text-blue-900";
    return "bg-gray-100 text-gray-500";
}

export function ClassificationMatrix({ projectId, classifications, requirements }: ClassificationMatrixProps) {
    const [localMappings, setLocalMappings] = React.useState(classifications);
    const [editingId, setEditingId] = React.useState<string | null>(null);

    React.useEffect(() => {
        setLocalMappings(classifications);
    }, [classifications]);

    const handleUpdate = (updated: TestCategoryMap) => {
        setLocalMappings(prev => prev.map(m => m.id === updated.id ? updated : m));
        setEditingId(null);
    };

    // Group mappings by requirement
    const mappingByReq: Record<string, Record<string, TestCategoryMap>> = {};
    requirements.forEach(req => {
        mappingByReq[req.id] = {};
    });

    localMappings.forEach(mapping => {
        if (mapping.requirement_id) {
            if (!mappingByReq[mapping.requirement_id]) {
                mappingByReq[mapping.requirement_id] = {};
            }
            mappingByReq[mapping.requirement_id][mapping.test_category] = mapping;
        }
    });

    // Calculate counts for bar chart
    const counts = CATEGORIES.reduce((acc, cat) => {
        acc[cat] = localMappings.filter(m => m.test_category === cat).length;
        return acc;
    }, {} as Record<string, number>);

    const maxCount = Math.max(...Object.values(counts), 1);

    const editingMapping = localMappings.find(m => m.id === editingId);

    return (
        <div className="flex flex-col gap-8">
            {/* Summary Chart */}
            <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
                <h4 className="text-sm font-semibold mb-4 text-gray-700 uppercase tracking-wider">Test Category Distribution</h4>
                <div className="flex flex-col gap-3">
                    {CATEGORIES.map(cat => (
                        <div key={cat} className="flex items-center gap-4 text-sm">
                            <div className="w-32 text-right capitalize text-gray-600">{cat}</div>
                            <div className="flex-1 h-6 bg-gray-100 rounded-md overflow-hidden relative">
                                <div
                                    className="h-full bg-blue-500 transition-all duration-500"
                                    style={{ width: `${(counts[cat] / maxCount) * 100}%` }}
                                />
                            </div>
                            <div className="w-8 text-right font-medium">{counts[cat]}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Heatmap Matrix */}
            <div className="rounded-lg border border-gray-200 bg-white shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-center">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="px-4 py-3 text-left font-medium text-gray-500 w-64 uppercase tracking-wider text-xs">Requirement</th>
                                {CATEGORIES.map(cat => (
                                    <th key={cat} className="px-2 py-3 font-medium text-gray-500 capitalize">{cat}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {requirements.map(req => (
                                <tr key={req.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-4 py-3 text-left">
                                        <div className="font-semibold text-gray-900 line-clamp-1" title={req.title}>{req.title}</div>
                                        <div className="text-xs text-gray-500 font-mono mt-0.5">{req.requirement_id}</div>
                                    </td>
                                    {CATEGORIES.map(cat => {
                                        const mapping = mappingByReq[req.id]?.[cat];
                                        return (
                                            <td key={cat} className="p-2 border-l border-gray-100 min-w-[80px]">
                                                {mapping ? (
                                                    <div
                                                        onClick={() => setEditingId(mapping.id)}
                                                        className={`w-full h-10 rounded flex items-center justify-center cursor-pointer transition-transform hover:scale-105 ${getIntensityClass(mapping.confidence)}`}
                                                        title={`Click to edit.\nConfidence: ${mapping.confidence}\nLayer: ${mapping.pipeline_layer}`}
                                                    >
                                                        {(mapping.confidence * 100).toFixed(0)}%
                                                    </div>
                                                ) : (
                                                    <div className="w-full h-10 bg-gray-50 rounded border border-dashed border-gray-200" />
                                                )}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                            {requirements.length === 0 && (
                                <tr>
                                    <td colSpan={CATEGORIES.length + 1} className="px-4 py-8 text-center text-gray-500">
                                        No mapping data available
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <Dialog open={!!editingId} onOpenChange={(open) => !open && setEditingId(null)}>
                <DialogContent className="max-w-2xl p-0">
                    {editingMapping && (
                        <ClassificationEditor
                            projectId={projectId}
                            classification={editingMapping}
                            onSave={handleUpdate}
                            onCancel={() => setEditingId(null)}
                        />
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}
