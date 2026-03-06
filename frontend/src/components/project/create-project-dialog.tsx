"use client";

import { useRef, useState } from "react";

interface Props {
  onClose: () => void;
  onSubmit: (formData: FormData) => void;
  isLoading: boolean;
}

export function CreateProjectDialog({ onClose, onSubmit, isLoading }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const fd = new FormData();
    fd.append("name", name);
    if (description) fd.append("description", description);
    if (fileRef.current?.files?.[0]) {
      fd.append("file", fileRef.current.files[0]);
    }
    onSubmit(fd);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-lg font-semibold">New Project</h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full rounded border px-3 py-2 text-sm"
              placeholder="My BRD Project"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
              rows={2}
              placeholder="Optional description..."
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">BRD File (PDF/DOCX)</label>
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.docx"
              className="text-sm"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded border px-4 py-2 text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!name || isLoading}
              className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? "Creating..." : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
