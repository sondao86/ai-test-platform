"use client";

import * as React from "react";
import { type Requirement } from "@/types/api";
import { updateRequirement } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";

interface RequirementEditorProps {
    projectId: string;
    requirement: Requirement;
    onSave: (updatedReq: Requirement) => void;
    onCancel: () => void;
}

export function RequirementEditor({ projectId, requirement, onSave, onCancel }: RequirementEditorProps) {
    const [title, setTitle] = React.useState(requirement.title);
    const [description, setDescription] = React.useState(requirement.description);
    const [priority, setPriority] = React.useState(requirement.priority);
    const [rules, setRules] = React.useState(requirement.business_rules?.join("\n") || "");
    const [kpis, setKpis] = React.useState(requirement.kpis?.join("\n") || "");

    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const { toast } = useToast();

    const handleSave = async () => {
        try {
            setIsSubmitting(true);
            const updated = await updateRequirement(projectId, requirement.id, {
                title,
                description,
                priority,
                business_rules: rules.split("\n").filter(r => r.trim() !== ""),
                kpis: kpis.split("\n").filter(k => k.trim() !== "")
            });
            toast({ title: "Requirement updated successfully", type: "success" });
            onSave(updated);
        } catch {
            toast({ title: "Failed to update requirement", type: "error" });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="flex flex-col gap-4 rounded-md border border-gray-200 bg-gray-50 p-4 w-full">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                    <label className="mb-1 block text-sm font-medium">Title</label>
                    <Input
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                    />
                </div>

                <div className="md:col-span-2">
                    <label className="mb-1 block text-sm font-medium">Description</label>
                    <Textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows={3}
                    />
                </div>

                <div>
                    <label className="mb-1 block text-sm font-medium">Priority</label>
                    <Select
                        value={priority}
                        onChange={(e) => setPriority(e.target.value)}
                    >
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </Select>
                </div>

                <div className="md:col-span-2">
                    <label className="mb-1 block text-sm font-medium">Business Rules (one per line)</label>
                    <Textarea
                        value={rules}
                        onChange={(e) => setRules(e.target.value)}
                        rows={4}
                        placeholder="E.g. Customer must have an email\nAmount > 0"
                    />
                </div>

                <div className="md:col-span-2">
                    <label className="mb-1 block text-sm font-medium">KPIs (one per line)</label>
                    <Textarea
                        value={kpis}
                        onChange={(e) => setKpis(e.target.value)}
                        rows={2}
                        placeholder="KPI-001\nKPI-002"
                    />
                </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t mt-2">
                <Button variant="ghost" size="sm" onClick={onCancel} disabled={isSubmitting}>
                    Cancel
                </Button>
                <Button variant="primary" size="sm" onClick={handleSave} disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : "Save"}
                </Button>
            </div>
        </div>
    );
}
