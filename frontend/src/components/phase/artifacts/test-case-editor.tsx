"use client";

import * as React from "react";
import { type TestCase } from "@/types/api";
import { updateTestCase } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";

interface TestCaseEditorProps {
    projectId: string;
    testCase: TestCase;
    onSave: (updated: TestCase) => void;
    onCancel: () => void;
}

const CATEGORIES = ["completeness", "consistency", "timeliness", "accuracy", "uniqueness", "validity"];
const SEVERITIES = ["critical", "high", "medium", "low"];
const TOOLS = ["dbt_test", "great_expectations", "custom_sql", "dbt_macro"];
const PIPELINE_LAYERS = ["staging", "intermediate", "mart"];

export function TestCaseEditor({ projectId, testCase, onSave, onCancel }: TestCaseEditorProps) {
    const [title, setTitle] = React.useState(testCase.title);
    const [description, setDescription] = React.useState(testCase.description);
    const [category, setCategory] = React.useState(testCase.test_category);
    const [layer, setLayer] = React.useState(testCase.pipeline_layer);
    const [tool, setTool] = React.useState(testCase.tool);
    const [sqlLogic, setSqlLogic] = React.useState(testCase.sql_logic || "");
    const [severity, setSeverity] = React.useState(testCase.severity);
    const [priority, setPriority] = React.useState(testCase.priority.toString());

    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const { toast } = useToast();

    const handleSave = async () => {
        try {
            setIsSubmitting(true);
            const updated = await updateTestCase(projectId, testCase.id, {
                title,
                description,
                test_category: category,
                pipeline_layer: layer,
                tool,
                sql_logic: sqlLogic || null,
                severity,
                priority: parseInt(priority, 10) || 1,
            });
            toast({ title: "Test Case updated successfully", type: "success" });
            onSave(updated);
        } catch {
            toast({ title: "Failed to update test case", type: "error" });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="flex flex-col gap-4 rounded-md border border-gray-200 bg-gray-50 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                    <label className="mb-1 block text-sm font-medium">Title</label>
                    <Input value={title} onChange={(e) => setTitle(e.target.value)} />
                </div>

                <div className="md:col-span-2">
                    <label className="mb-1 block text-sm font-medium">Description</label>
                    <Textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
                </div>

                <div>
                    <label className="mb-1 block text-sm font-medium">Category</label>
                    <Select value={category} onChange={e => setCategory(e.target.value)}>
                        {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </Select>
                </div>

                <div>
                    <label className="mb-1 block text-sm font-medium">Pipeline Layer</label>
                    <Select value={layer} onChange={e => setLayer(e.target.value)}>
                        {PIPELINE_LAYERS.map(l => <option key={l} value={l}>{l}</option>)}
                    </Select>
                </div>

                <div>
                    <label className="mb-1 block text-sm font-medium">Tool</label>
                    <Select value={tool} onChange={e => setTool(e.target.value)}>
                        {TOOLS.map(t => <option key={t} value={t}>{t}</option>)}
                    </Select>
                </div>

                <div>
                    <label className="mb-1 block text-sm font-medium">Severity</label>
                    <Select value={severity} onChange={e => setSeverity(e.target.value)}>
                        {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
                    </Select>
                </div>

                <div>
                    <label className="mb-1 block text-sm font-medium">Priority (1 = high, 5 = low)</label>
                    <Input type="number" min="1" max="5" value={priority} onChange={e => setPriority(e.target.value)} />
                </div>

                <div className="md:col-span-2 mt-4">
                    <label className="mb-1 block text-sm font-medium">SQL Logic (optional)</label>
                    <Textarea
                        value={sqlLogic}
                        onChange={e => setSqlLogic(e.target.value)}
                        rows={5}
                        className="font-mono text-xs"
                        placeholder="SELECT * FROM table WHERE condition is false..."
                    />
                </div>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t mt-2">
                <Button variant="ghost" size="sm" onClick={onCancel} disabled={isSubmitting}>Cancel</Button>
                <Button variant="primary" size="sm" onClick={handleSave} disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : "Save"}
                </Button>
            </div>
        </div>
    );
}
