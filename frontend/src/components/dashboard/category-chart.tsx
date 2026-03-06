"use client";

import type { TestCase } from "@/types/api";

const CATEGORIES = ["completeness", "consistency", "timeliness", "accuracy", "uniqueness", "validity"];

interface CategoryChartProps {
    testCases: TestCase[];
}

export function CategoryChart({ testCases }: CategoryChartProps) {
    const counts = CATEGORIES.reduce((acc, cat) => {
        acc[cat] = testCases.filter((tc) => tc.test_category === cat).length;
        return acc;
    }, {} as Record<string, number>);

    const maxCount = Math.max(...Object.values(counts), 1);

    return (
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h3 className="mb-6 text-base font-semibold text-gray-900">Test Cases by Category</h3>
            <div className="flex flex-col gap-4">
                {CATEGORIES.map((cat) => {
                    const count = counts[cat];
                    const percentage = (count / maxCount) * 100;

                    return (
                        <div key={cat} className="flex items-center gap-4 text-sm">
                            <div className="w-24 text-right capitalize text-gray-600">{cat}</div>
                            <div className="relative flex h-6 w-full items-center rounded-md bg-gray-100 overflow-hidden">
                                <div
                                    className="h-full bg-blue-500 transition-all duration-500 ease-in-out"
                                    style={{ width: `${percentage}%` }}
                                />
                            </div>
                            <div className="w-8 text-right font-medium text-gray-900">{count}</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
