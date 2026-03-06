"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    LayoutDashboard,
    FileText,
    ListChecks,
    Grid,
    Target,
    Bot,
    History,
    Menu,
    X
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface SidebarProps {
    projectId: string;
    className?: string;
}

export function Sidebar({ projectId, className }: SidebarProps) {
    const pathname = usePathname();
    const [isOpen, setIsOpen] = React.useState(false);

    const navItems = [
        { label: "Overview", href: `/projects/${projectId}`, icon: LayoutDashboard, exact: true },
        { label: "Phase 1: Chunks", href: `/projects/${projectId}/phases/1`, icon: FileText },
        { label: "Phase 2: Requirements", href: `/projects/${projectId}/phases/2`, icon: ListChecks },
        { label: "Phase 3: Classification", href: `/projects/${projectId}/phases/3`, icon: Grid },
        { label: "Phase 4: Test Cases", href: `/projects/${projectId}/phases/4`, icon: Target },
        { label: "Agent Reviews", href: `/projects/${projectId}/reviews`, icon: Bot },
        { label: "History", href: `/projects/${projectId}/history`, icon: History },
        { label: "Dashboard", href: `/projects/${projectId}/dashboard`, icon: LayoutDashboard },
    ];

    const NavLinks = () => (
        <div className="flex flex-col gap-1 w-full">
            {navItems.map((item) => {
                const isActive = item.exact
                    ? pathname === item.href
                    : pathname.startsWith(item.href);

                return (
                    <Link
                        key={item.href}
                        href={item.href}
                        onClick={() => setIsOpen(false)}
                        className={cn(
                            "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                            isActive
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-600 hover:bg-gray-50 justify-start hover:text-gray-900"
                        )}
                    >
                        <item.icon className={cn("h-4 w-4 shrink-0", isActive ? "text-gray-900" : "text-gray-400")} />
                        {item.label}
                    </Link>
                );
            })}
        </div>
    );

    return (
        <>
            <div className="md:hidden mb-4 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wider">Project Menu</h2>
                <Button variant="ghost" size="sm" onClick={() => setIsOpen(!isOpen)}>
                    {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </Button>
            </div>

            <div className={cn(
                "flex flex-col gap-6 md:block w-full",
                isOpen ? "block" : "hidden",
                className
            )}>
                <nav className="sticky top-6 w-full md:w-56 shrink-0 border-r border-transparent md:border-gray-100 md:pr-4">
                    <div className="hidden md:block mb-4">
                        <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider pl-3">Project Navigator</h2>
                    </div>
                    <NavLinks />
                </nav>
            </div>
        </>
    );
}
