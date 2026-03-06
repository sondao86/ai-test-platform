"use client";

import * as React from "react";
import { type TestCategoryMap } from "@/types/api";
import { updateClassification } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";

interface ClassificationEditorProps {
    projectId: string;
    classification: TestCategoryMap;
    onSave: (updated: TestCategoryMap) => void;
    onCancel: () => void;
}

const CATEGORIES = [
    "completeness",
    "consistency",
    "timeliness",
    "accuracy",
    "uniqueness",
    "validity"
];

const PIPELINE_LAYERS = ["staging", "intermediate", "mart"];
const TOOLS = ["dbt_test", "great_expectations", "custom_sql", "dbt_macro"];

export function ClassificationEditor({ projectId, classification, onSave, onCancel }: ClassificationEditorProps) {
    const [category, setCategory] = React.useState(classification.test_category);
    const [subCategory, setSubCategory] = React.useState(classification.sub_category || "");
    const [rationale, setRationale] = React.useState(classification.rationale || "");
    const [layer, setLayer] = React.useState(classification.pipeline_layer || "staging");
    const [tool, setTool] = React.useState(classification.tool_suggestion || "dbt_test");

    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const { toast } = useToast();

    const handleSave = async () => {
        try {
            setIsSubmitting(true);
            const updated = await updateClassification(projectId, classification.id, {
                test_category: category,
                sub_category: subCategory || null,
                rationale,
                pipeline_layer: layer,
                tool_suggestion: tool
            });
            toast({ title: "Classification updated", type: "success" });
            onSave(updated);
        } catch {
            toast({ title: "Failed to update classification", type: "error" });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="flex flex-col gap-4 p-4">
            <h3 className="text-lg font-semibold border-b pb-2">Edit Classification Mapping</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="mb-1 block text-sm font-medium">Test Category</label>
                    <Select value={category} onChange={e => setCategory(e.target.value)}>
                        {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </Select>
                </div>

                <div>
                    <label className="mb-1 block text-sm font-medium">Sub Category (optional)</label>
                    <Input value={subCategory} onChange={e => setSubCategory(e.target.value)} placeholder="e.g. range_check" />
                </div>

                <div>
                    <label className="mb-1 block text-sm font-medium">Pipeline Layer</label>
                    <Select value={layer} onChange={e => setLayer(e.target.value)}>
                        {PIPELINE_LAYERS.map(l => <option key={l} value={l}>{l}</option>)}
                    </Select>
                </div>

                <div>
                    <label className="mb-1 block text-sm font-medium">Tool Suggestion</label>
                    <Select value={tool} onChange={e => setTool(e.target.value)}>
                        {TOOLS.map(t => <option key={t} value={t}>{t}</option>)}
                    </Select>
                </div>

                <div className="md:col-span-2">
                    <label className="mb-1 block text-sm font-medium">Rationale</label>
                    <Textarea
                        value={rationale}
                        onChange={e => setRationale(e.target.value)}
                        rows={3}
                        placeholder="Explain why this category applies..."
                    />
                </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
                <Button variant="ghost" onClick={onCancel} disabled={isSubmitting}>Cancel</Button>
                <Button onClick={handleSave} disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : "Save"}
                </Button>
            </div>
        </div>
    );
}
