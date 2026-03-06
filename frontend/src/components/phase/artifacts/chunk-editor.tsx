"use client";

import * as React from "react";
import { type BrdChunk } from "@/types/api";
import { updateChunk } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";

interface ChunkEditorProps {
    projectId: string;
    chunk: BrdChunk;
    onSave: (updatedChunk: BrdChunk) => void;
}

const SECTION_TYPES = [
    "executive_summary",
    "business_context",
    "functional_requirement",
    "non_functional_requirement",
    "data_requirement",
    "kpi_definition",
    "business_rule",
    "acceptance_criteria",
    "dependency",
    "glossary",
    "appendix",
    "other",
];

export function ChunkEditor({ projectId, chunk, onSave }: ChunkEditorProps) {
    const [isEditing, setIsEditing] = React.useState(false);
    const [title, setTitle] = React.useState(chunk.section_title);
    const [content, setContent] = React.useState(chunk.content);
    const [sectionType, setSectionType] = React.useState(chunk.section_type);
    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const { toast } = useToast();

    // Reset state if chunk changes externally or edit is cancelled
    React.useEffect(() => {
        setTitle(chunk.section_title);
        setContent(chunk.content);
        setSectionType(chunk.section_type);
    }, [chunk, isEditing]);

    const handleSave = async () => {
        try {
            setIsSubmitting(true);
            const updated = await updateChunk(projectId, chunk.id, {
                section_title: title,
                content,
                section_type: sectionType,
            });
            toast({ title: "Chunk updated successfully", type: "success" });
            setIsEditing(false);
            onSave(updated);
        } catch {
            toast({ title: "Failed to update chunk", type: "error" });
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!isEditing) {
        return (
            <div className="flex flex-col gap-3 rounded-md border border-gray-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start gap-4">
                    <div>
                        <h4 className="font-semibold text-gray-900 leading-tight mb-1">{chunk.section_title}</h4>
                        <span className="inline-block rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-blue-700">
                            {chunk.section_type.replace(/_/g, " ")}
                        </span>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)}>
                        Edit
                    </Button>
                </div>
                <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md whitespace-pre-wrap font-serif leading-relaxed border border-gray-100">
                    {chunk.content}
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-4 rounded-md border-2 border-blue-200 bg-blue-50/30 p-4 shadow-sm">
            <div>
                <label className="mb-1 block text-sm font-medium">Section Title</label>
                <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Enter title..."
                />
            </div>

            <div>
                <label className="mb-1 block text-sm font-medium">Section Type</label>
                <Select
                    value={sectionType}
                    onChange={(e) => setSectionType(e.target.value)}
                >
                    {SECTION_TYPES.map(t => (
                        <option key={t} value={t}>{t}</option>
                    ))}
                </Select>
            </div>

            <div>
                <label className="mb-1 block text-sm font-medium">Content</label>
                <Textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    rows={6}
                />
            </div>

            <div className="flex justify-end gap-2 pt-2">
                <Button variant="ghost" size="sm" onClick={() => setIsEditing(false)} disabled={isSubmitting}>
                    Cancel
                </Button>
                <Button variant="primary" size="sm" onClick={handleSave} disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : "Save"}
                </Button>
            </div>
        </div>
    );
}
