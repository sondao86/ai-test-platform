"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listProjects, createProject, deleteProject } from "@/lib/api";
import { ProjectCard } from "@/components/project/project-card";
import { CreateProjectDialog } from "@/components/project/create-project-dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useState } from "react";

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: listProjects,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteProject,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects"] }),
  });

  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setShowCreate(false);
    },
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Projects</h1>
        <button
          onClick={() => setShowCreate(true)}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
        >
          New Project
        </button>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
        </div>
      )}

      {data && data.items.length === 0 && (
        <p className="text-gray-500">No projects yet. Create one to get started.</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data?.items.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            onDelete={() => deleteMutation.mutate(project.id)}
          />
        ))}
      </div>

      {showCreate && (
        <CreateProjectDialog
          onClose={() => setShowCreate(false)}
          onSubmit={(formData) => createMutation.mutate(formData)}
          isLoading={createMutation.isPending}
        />
      )}
    </div>
  );
}
