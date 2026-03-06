import * as React from "react";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";

export interface BreadcrumbItem {
    label: string;
    href?: string;
    active?: boolean;
}

export interface BreadcrumbsProps {
    items: BreadcrumbItem[];
    className?: string;
}

export function Breadcrumbs({ items, className }: BreadcrumbsProps) {
    return (
        <nav className={cn("flex text-sm text-gray-500", className)} aria-label="Breadcrumb">
            <ol className="flex items-center space-x-2">
                <li>
                    <Link href="/" className="hover:text-gray-900 flex items-center">
                        <Home className="h-4 w-4" />
                        <span className="sr-only">Home</span>
                    </Link>
                </li>

                {items.map((item, index) => (
                    <li key={index} className="flex items-center">
                        <ChevronRight className="h-4 w-4 mx-1 flex-shrink-0 text-gray-400" />

                        {item.href && !item.active ? (
                            <Link
                                href={item.href}
                                className="hover:text-gray-900 transition-colors capitalize"
                            >
                                {item.label}
                            </Link>
                        ) : (
                            <span
                                className={cn(
                                    "capitalize",
                                    item.active ? "font-medium text-gray-900" : ""
                                )}
                                aria-current={item.active ? "page" : undefined}
                            >
                                {item.label}
                            </span>
                        )}
                    </li>
                ))}
            </ol>
        </nav>
    );
}
