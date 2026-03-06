import { FileText, ListChecks, Grid, Target } from "lucide-react";

interface StatsGridProps {
    chunkCount: number;
    reqCount: number;
    classCount: number;
    testCaseCount: number;
}

export function StatsGrid({ chunkCount, reqCount, classCount, testCaseCount }: StatsGridProps) {
    const stats = [
        { label: "Chunks Parsed", value: chunkCount, icon: FileText, color: "text-purple-600", bg: "bg-purple-100" },
        { label: "Requirements", value: reqCount, icon: ListChecks, color: "text-blue-600", bg: "bg-blue-100" },
        { label: "Classifications", value: classCount, icon: Grid, color: "text-indigo-600", bg: "bg-indigo-100" },
        { label: "Test Cases", value: testCaseCount, icon: Target, color: "text-green-600", bg: "bg-green-100" },
    ];

    return (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat, i) => (
                <div key={i} className="flex items-center gap-4 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-full ${stat.bg}`}>
                        <stat.icon className={`h-6 w-6 ${stat.color}`} />
                    </div>
                    <div>
                        <div className="text-sm font-medium text-gray-500">{stat.label}</div>
                        <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                    </div>
                </div>
            ))}
        </div>
    );
}
