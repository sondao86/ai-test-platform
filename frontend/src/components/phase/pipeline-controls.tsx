"use client";

import { useState } from "react";
import type { Project, PipelineStatus } from "@/types/api";

interface Props {
  project: Project;
  pipelineStatus: PipelineStatus | null;
  onStart: () => void;
  onApprove: () => void;
  onRevise: (feedback: string) => void;
  isStarting: boolean;
  isDeciding: boolean;
}

export function PipelineControls({
  project,
  pipelineStatus,
  onStart,
  onApprove,
  onRevise,
  isStarting,
  isDeciding,
}: Props) {
  const [showRevise, setShowRevise] = useState(false);
  const [feedback, setFeedback] = useState("");

  const canStart = project.status === "created" && project.file_name;
  const isAwaiting = pipelineStatus?.status === "awaiting_user";

  if (showRevise) {
    return (
      <div className="flex flex-col gap-2">
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Describe what should be revised..."
          className="w-64 rounded border px-3 py-2 text-sm"
          rows={3}
        />
        <div className="flex gap-2">
          <button
            onClick={() => {
              onRevise(feedback);
              setShowRevise(false);
              setFeedback("");
            }}
            disabled={isDeciding || !feedback}
            className="rounded bg-yellow-600 px-3 py-1 text-sm text-white hover:bg-yellow-700 disabled:opacity-50"
          >
            {isDeciding ? "Submitting..." : "Submit Revision"}
          </button>
          <button
            onClick={() => setShowRevise(false)}
            className="rounded border px-3 py-1 text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-2">
      {canStart && (
        <button
          onClick={onStart}
          disabled={isStarting}
          className="rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 disabled:opacity-50"
        >
          {isStarting ? "Starting..." : "Start Pipeline"}
        </button>
      )}
      {isAwaiting && (
        <>
          <button
            onClick={onApprove}
            disabled={isDeciding}
            className="rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 disabled:opacity-50"
          >
            {isDeciding ? "..." : "Approve"}
          </button>
          <button
            onClick={() => setShowRevise(true)}
            className="rounded-lg bg-yellow-600 px-4 py-2 text-sm text-white hover:bg-yellow-700"
          >
            Request Revision
          </button>
        </>
      )}
    </div>
  );
}
