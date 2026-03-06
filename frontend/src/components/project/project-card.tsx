import Link from "next/link";
import type { Project } from "@/types/api";
import { STATUS_COLORS, PHASE_NAMES, formatDate } from "@/lib/utils";

interface Props {
  project: Project;
  onDelete: () => void;
}

export function ProjectCard({ project, onDelete }: Props) {
  return (
    <div className="rounded-lg border bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <Link href={`/projects/${project.id}`} className="hover:underline">
          <h3 className="font-semibold">{project.name}</h3>
        </Link>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[project.status] || "bg-gray-100"}`}
        >
          {project.status}
        </span>
      </div>

      {project.description && (
        <p className="mt-1 text-sm text-gray-600 line-clamp-2">{project.description}</p>
      )}

      <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
        <span>
          {project.current_phase > 0
            ? `Phase ${project.current_phase}: ${PHASE_NAMES[project.current_phase]}`
            : "Not started"}
        </span>
        <span>{formatDate(project.created_at)}</span>
      </div>

      <div className="mt-3 flex gap-2">
        <Link
          href={`/projects/${project.id}`}
          className="rounded bg-blue-50 px-3 py-1 text-xs text-blue-700 hover:bg-blue-100"
        >
          Open
        </Link>
        <button
          onClick={onDelete}
          className="rounded bg-red-50 px-3 py-1 text-xs text-red-700 hover:bg-red-100"
        >
          Archive
        </button>
      </div>
    </div>
  );
}
