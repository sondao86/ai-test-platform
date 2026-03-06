import { Sidebar } from "@/components/layout/sidebar";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { ErrorBoundary } from "@/components/error-boundary";

export default async function ProjectLayout({
    children,
    params,
}: {
    children: React.ReactNode;
    params: Promise<{ id: string }>;
}) {
    const resolvedParams = await params;
    const projectId = resolvedParams.id;

    return (
        <div className="flex flex-col gap-6">
            <Breadcrumbs
                items={[
                    { label: "Projects", href: "/projects" },
                    { label: "Project Details", active: true },
                ]}
            />
            <div className="flex flex-col md:flex-row gap-8 items-start">
                <Sidebar projectId={projectId} />
                <div className="flex-1 w-full min-w-0">
                    <ErrorBoundary>
                        {children}
                    </ErrorBoundary>
                </div>
            </div>
        </div>
    );
}
