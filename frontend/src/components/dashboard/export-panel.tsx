"use client";

import type { TestCase } from "@/types/api";
import { Download, FileCode, FileJson } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ExportPanelProps {
    projectId: string;
    testCases: TestCase[];
}

export function ExportPanel({ projectId, testCases }: ExportPanelProps) {
    const handleExportJSON = () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(testCases, null, 2));
        const downloadAnchorNode = document.createElement("a");
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `project-${projectId}-test-cases.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    const handleExportYAML = () => {
        // Combine all YAML snippets
        const yamlContents = testCases
            .filter((tc) => tc.dbt_test_yaml)
            .map((tc) => `# Target: ${tc.test_id} - ${tc.title}\n${tc.dbt_test_yaml}`)
            .join("\n\n");

        const dataStr = "data:text/yaml;charset=utf-8," + encodeURIComponent(yamlContents || "# No YAML configs generated.");
        const downloadAnchorNode = document.createElement("a");
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `project-${projectId}-dbt-tests.yml`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    return (
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h3 className="mb-2 text-base font-semibold text-gray-900">Export Artifacts</h3>
            <p className="mb-6 text-sm text-gray-500">Download the generated test cases to use in your data pipelines.</p>

            <div className="flex flex-col gap-3">
                <Button variant="outline" className="w-full justify-start" onClick={handleExportJSON}>
                    <FileJson className="mr-2 h-4 w-4" />
                    Export JSON Metadata
                    <Download className="ml-auto h-4 w-4 text-gray-400" />
                </Button>
                <Button variant="outline" className="w-full justify-start" onClick={handleExportYAML}>
                    <FileCode className="mr-2 h-4 w-4" />
                    Export dbt YAML Concat
                    <Download className="ml-auto h-4 w-4 text-gray-400" />
                </Button>
            </div>
        </div>
    );
}
