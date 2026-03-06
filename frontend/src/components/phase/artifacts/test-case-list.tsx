"use client";

import * as React from "react";
import { type TestCase } from "@/types/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CodeBlock } from "@/components/ui/code-block";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Download, Edit2, PlayCircle, Eye, Search } from "lucide-react";
import { TestCaseEditor } from "./test-case-editor";
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible";

interface TestCaseListProps {
    projectId: string;
    testCases: TestCase[];
}

const CATEGORIES = ["completeness", "consistency", "timeliness", "accuracy", "uniqueness", "validity"];

function getSeverityColor(sev: string) {
    if (sev === "critical" || sev === "high") return "bg-red-100 text-red-800 border-red-300";
    if (sev === "medium") return "bg-yellow-100 text-yellow-800 border-yellow-300";
    return "bg-green-100 text-green-800 border-green-300";
}

export function TestCaseList({ projectId, testCases }: TestCaseListProps) {
    const [localTests, setLocalTests] = React.useState(testCases);
    const [editingId, setEditingId] = React.useState<string | null>(null);
    const [searchQuery, setSearchQuery] = React.useState("");

    React.useEffect(() => {
        setLocalTests(testCases);
    }, [testCases]);

    const handleUpdate = (updated: TestCase) => {
        setLocalTests(prev => prev.map(t => t.id === updated.id ? updated : t));
        setEditingId(null);
    };

    const filteredTests = React.useMemo(() => {
        if (!searchQuery.trim()) return localTests;
        const lowerQuery = searchQuery.toLowerCase();
        return localTests.filter(tc =>
            tc.title.toLowerCase().includes(lowerQuery) ||
            tc.description?.toLowerCase().includes(lowerQuery) ||
            tc.test_id.toLowerCase().includes(lowerQuery)
        );
    }, [localTests, searchQuery]);

    const currentCategoryTestCases = (category: string) => {
        return filteredTests.filter(t => t.test_category === category).sort((a, b) => a.priority - b.priority);
    };

    const handleExport = () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(filteredTests, null, 2));
        const downloadAnchorNode = document.createElement("a");
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `project-${projectId}-test-cases.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    if (!localTests?.length) {
        return <div className="text-sm text-gray-500 italic p-4">No test cases generated yet.</div>;
    }

    const defaultTab = CATEGORIES.find(cat => currentCategoryTestCases(cat).length > 0) || CATEGORIES[0];

    return (
        <div className="flex flex-col gap-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div className="w-full sm:max-w-md relative text-gray-600 focus-within:text-gray-900">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" />
                    <input
                        type="search"
                        placeholder="Search test cases by ID, title, or description..."
                        className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
                <Button variant="outline" size="sm" onClick={handleExport} className="shrink-0">
                    <Download className="h-4 w-4 mr-2" />
                    Export JSON
                </Button>
            </div>

            <Tabs defaultValue={defaultTab} className="w-full">
                <TabsList className="mb-4 flex flex-wrap max-w-full justify-start h-auto gap-1 bg-transparent">
                    {CATEGORIES.map(cat => {
                        const count = currentCategoryTestCases(cat).length;
                        if (count === 0) return null;
                        return (
                            <TabsTrigger key={cat} value={cat} className="capitalize data-[state=active]:bg-gray-900 data-[state=active]:text-white">
                                {cat}
                                <span className="ml-2 rounded-full bg-gray-200 text-gray-700 px-2 py-0.5 text-xs data-[state=active]:bg-gray-700 data-[state=active]:text-white">
                                    {count}
                                </span>
                            </TabsTrigger>
                        );
                    })}
                </TabsList>

                {CATEGORIES.map(cat => (
                    <TabsContent key={cat} value={cat}>
                        <div className="flex flex-col gap-4">
                            {currentCategoryTestCases(cat).map(tc => (
                                <div key={tc.id} className="rounded-lg border border-gray-200 bg-white overflow-hidden shadow-sm">
                                    {editingId === tc.id ? (
                                        <TestCaseEditor
                                            projectId={projectId}
                                            testCase={tc}
                                            onSave={handleUpdate}
                                            onCancel={() => setEditingId(null)}
                                        />
                                    ) : (
                                        <Collapsible>
                                            <div className="p-4 flex items-start justify-between sm:items-center hover:bg-gray-50 transition-colors">
                                                <CollapsibleTrigger className="flex flex-1 flex-col sm:flex-row sm:items-center gap-3 text-left">
                                                    <div className="font-mono text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-1 rounded inline-flex shrink-0">
                                                        {tc.test_id}
                                                    </div>
                                                    <div className="font-semibold text-gray-900 flex-1">{tc.title}</div>

                                                    <div className="flex items-center gap-2 mt-2 sm:mt-0 flex-wrap">
                                                        <Badge variant="outline" className={`border text-[10px] uppercase font-bold py-0 h-5 ${getSeverityColor(tc.severity)}`}>
                                                            {tc.severity}
                                                        </Badge>
                                                        <Badge variant="outline" className="text-xs bg-gray-50 capitalize">
                                                            {tc.pipeline_layer}
                                                        </Badge>
                                                        <Badge variant="outline" className="text-xs bg-indigo-50 text-indigo-700 border-indigo-200 uppercase tracking-wider">
                                                            <PlayCircle className="h-3 w-3 mr-1" />
                                                            {tc.tool}
                                                        </Badge>
                                                    </div>
                                                </CollapsibleTrigger>

                                                <div className="flex items-center ml-4 shrink-0">
                                                    <Button variant="ghost" size="sm" onClick={() => setEditingId(tc.id)}>
                                                        <Edit2 className="h-4 w-4" />
                                                        <span className="sr-only">Edit</span>
                                                    </Button>
                                                </div>
                                            </div>

                                            <CollapsibleContent>
                                                <div className="p-5 border-t border-gray-100 bg-gray-50 space-y-4">
                                                    <p className="text-sm text-gray-700 mb-4">{tc.description}</p>

                                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                                        {tc.sql_logic && (
                                                            <div className="space-y-2 lg:col-span-2">
                                                                <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1">
                                                                    <Eye className="h-3 w-3" /> SQL Logic Preview
                                                                </h5>
                                                                <CodeBlock code={tc.sql_logic} language="sql" className="max-h-64" />
                                                            </div>
                                                        )}

                                                        {tc.dbt_test_yaml && (
                                                            <div className="space-y-2">
                                                                <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">DBT YAML Configuration</h5>
                                                                <CodeBlock code={tc.dbt_test_yaml} language="yaml" className="max-h-64" />
                                                            </div>
                                                        )}

                                                        {tc.great_expectations_config && (
                                                            <div className="space-y-2">
                                                                <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Great Expectations Config</h5>
                                                                <CodeBlock code={JSON.stringify(tc.great_expectations_config, null, 2)} language="json" className="max-h-64" />
                                                            </div>
                                                        )}
                                                    </div>

                                                    <div className="flex justify-between items-center pt-4 mt-6 border-t border-gray-200">
                                                        <div className="text-xs text-gray-500 font-medium">Priority Context</div>
                                                        <div className="flex gap-4">
                                                            <div className="text-xs text-gray-500"><strong>Priority:</strong> {tc.priority}</div>
                                                            <div className="text-xs text-gray-500"><strong>SLA:</strong> {tc.sla_seconds ? `${tc.sla_seconds}s` : 'N/A'}</div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </CollapsibleContent>
                                        </Collapsible>
                                    )}
                                </div>
                            ))}
                        </div>
                    </TabsContent>
                ))}
            </Tabs>

            {filteredTests.length === 0 && searchQuery && (
                <div className="text-center p-8 text-gray-500 bg-gray-50 rounded-lg border border-dashed">
                    No test cases matching &quot;{searchQuery}&quot;
                </div>
            )}
        </div>
    );
}
