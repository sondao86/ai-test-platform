"use client";

import * as React from "react";
import { type Requirement } from "@/types/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, ChevronDown, ChevronUp, Edit2 } from "lucide-react";
import { RequirementEditor } from "./requirement-editor";

interface RequirementTableProps {
    projectId: string;
    requirements: Requirement[];
}

function getPriorityColor(priority: string) {
    switch (priority.toLowerCase()) {
        case "high":
        case "critical":
            return "bg-red-100 text-red-800 border-red-300";
        case "medium":
            return "bg-yellow-100 text-yellow-800 border-yellow-300";
        case "low":
            return "bg-green-100 text-green-800 border-green-300";
        default:
            return "bg-gray-100 text-gray-800 border-gray-300";
    }
}

export function RequirementTable({ projectId, requirements }: RequirementTableProps) {
    const [localReqs, setLocalReqs] = React.useState(requirements);
    const [search, setSearch] = React.useState("");
    const [expandedId, setExpandedId] = React.useState<string | null>(null);
    const [editingId, setEditingId] = React.useState<string | null>(null);
    const [sortField, setSortField] = React.useState<"req_id" | "title" | "priority" | "rules" | "kpis">("req_id");
    const [sortAsc, setSortAsc] = React.useState(true);

    React.useEffect(() => {
        setLocalReqs(requirements);
    }, [requirements]);

    const handleUpdate = (updatedReq: Requirement) => {
        setLocalReqs(prev => prev.map(r => r.id === updatedReq.id ? updatedReq : r));
        setEditingId(null);
    };

    const handleSort = (field: "req_id" | "title" | "priority" | "rules" | "kpis") => {
        if (sortField === field) setSortAsc(!sortAsc);
        else {
            setSortField(field);
            setSortAsc(true);
        }
    };

    const getPriorityWeight = (p: string) => {
        const lp = p.toLowerCase();
        if (lp === "critical" || lp === "high") return 3;
        if (lp === "medium") return 2;
        return 1;
    };

    const filteredAndSorted = localReqs.filter(r =>
        r.title.toLowerCase().includes(search.toLowerCase()) ||
        r.requirement_id.toLowerCase().includes(search.toLowerCase())
    );

    filteredAndSorted.sort((a, b) => {
        let comp = 0;
        if (sortField === "req_id") comp = a.requirement_id.localeCompare(b.requirement_id);
        else if (sortField === "title") comp = a.title.localeCompare(b.title);
        else if (sortField === "priority") {
            comp = getPriorityWeight(b.priority) - getPriorityWeight(a.priority); // descending priority by default
        }
        else if (sortField === "rules") comp = (a.business_rules?.length || 0) - (b.business_rules?.length || 0);
        else if (sortField === "kpis") comp = (a.kpis?.length || 0) - (b.kpis?.length || 0);

        return sortAsc ? comp : -comp;
    });

    if (!localReqs?.length) {
        return <div className="text-sm text-gray-500 italic p-4">No requirements generated yet.</div>;
    }

    return (
        <div className="flex flex-col gap-4">
            <div className="relative w-full max-w-sm">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                <Input
                    placeholder="Search by ID or title..."
                    className="pl-8"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
            </div>

            <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-gray-50 text-gray-500">
                            <tr>
                                <th className="px-4 py-3 font-medium cursor-pointer hover:bg-gray-100" onClick={() => handleSort("req_id")}>
                                    <div className="flex items-center gap-1">ID {sortField === "req_id" && (sortAsc ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}</div>
                                </th>
                                <th className="px-4 py-3 font-medium cursor-pointer hover:bg-gray-100" onClick={() => handleSort("title")}>
                                    <div className="flex items-center gap-1">Title {sortField === "title" && (sortAsc ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}</div>
                                </th>
                                <th className="px-4 py-3 font-medium cursor-pointer hover:bg-gray-100" onClick={() => handleSort("priority")}>
                                    <div className="flex items-center gap-1">Priority {sortField === "priority" && (sortAsc ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}</div>
                                </th>
                                <th className="px-4 py-3 font-medium text-center cursor-pointer hover:bg-gray-100" onClick={() => handleSort("rules")}>
                                    <div className="flex items-center justify-center gap-1">Rules {sortField === "rules" && (sortAsc ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}</div>
                                </th>
                                <th className="px-4 py-3 font-medium text-center cursor-pointer hover:bg-gray-100" onClick={() => handleSort("kpis")}>
                                    <div className="flex items-center justify-center gap-1">KPIs {sortField === "kpis" && (sortAsc ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}</div>
                                </th>
                                <th className="px-4 py-3 w-10"></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredAndSorted.map((req) => (
                                <React.Fragment key={req.id}>
                                    <tr
                                        className={`hover:bg-gray-50 cursor-pointer transition-colors ${expandedId === req.id || editingId === req.id ? 'bg-gray-50' : ''}`}
                                        onClick={() => {
                                            if (editingId !== req.id) {
                                                setExpandedId(expandedId === req.id ? null : req.id);
                                            }
                                        }}
                                    >
                                        <td className="px-4 py-3 font-mono text-xs font-semibold text-gray-900">{req.requirement_id}</td>
                                        <td className="px-4 py-3 font-medium text-gray-900 line-clamp-1">{req.title}</td>
                                        <td className="px-4 py-3">
                                            <div className={`px-2 py-0.5 mt-0.5 inline-flex text-[10px] font-bold uppercase tracking-wider rounded border ${getPriorityColor(req.priority)}`}>
                                                {req.priority}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-center text-gray-600">{req.business_rules?.length || 0}</td>
                                        <td className="px-4 py-3 text-center text-gray-600">{req.kpis?.length || 0}</td>
                                        <td className="px-4 py-3 text-right">
                                            <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${expandedId === req.id ? 'rotate-180' : ''}`} />
                                        </td>
                                    </tr>

                                    {/* Expanded Detail Panel */}
                                    {(expandedId === req.id || editingId === req.id) && (
                                        <tr>
                                            <td colSpan={6} className="bg-gray-50 p-0 border-t-0">
                                                <div className="p-4 pt-1 shadow-inner ring-1 ring-inset ring-black/5">
                                                    {editingId === req.id ? (
                                                        <RequirementEditor
                                                            projectId={projectId}
                                                            requirement={req}
                                                            onSave={handleUpdate}
                                                            onCancel={() => setEditingId(null)}
                                                        />
                                                    ) : (
                                                        <div className="flex flex-col gap-4 rounded-md border border-gray-200 bg-white p-4 items-start">
                                                            <div className="flex w-full justify-between items-start">
                                                                <div>
                                                                    <h4 className="font-semibold text-gray-900 mb-1">{req.title}</h4>
                                                                    <p className="text-sm text-gray-700">{req.description}</p>
                                                                </div>
                                                                <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setEditingId(req.id); }}>
                                                                    <Edit2 className="h-4 w-4 mr-2" />
                                                                    Edit
                                                                </Button>
                                                            </div>

                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full text-sm mt-2">
                                                                {req.business_rules && req.business_rules.length > 0 && (
                                                                    <div>
                                                                        <h5 className="font-medium text-gray-900 mb-2">Business Rules</h5>
                                                                        <ul className="list-disc pl-5 text-gray-600 space-y-1">
                                                                            {req.business_rules.map((rule, i) => <li key={i}>{rule}</li>)}
                                                                        </ul>
                                                                    </div>
                                                                )}

                                                                {req.kpis && req.kpis.length > 0 && (
                                                                    <div>
                                                                        <h5 className="font-medium text-gray-900 mb-2">KPIs</h5>
                                                                        <div className="flex flex-wrap gap-2">
                                                                            {req.kpis.map((kpi, i) => (
                                                                                <Badge key={i} variant="outline" className="text-xs bg-gray-50">{kpi}</Badge>
                                                                            ))}
                                                                        </div>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))}
                            {filteredAndSorted.length === 0 && (
                                <tr>
                                    <td colSpan={6} className="px-4 py-8 text-center text-sm text-gray-500">
                                        No requirements found matching &quot;{search}&quot;
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
