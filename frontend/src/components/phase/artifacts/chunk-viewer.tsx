"use client";

import * as React from "react";
import { type BrdChunk } from "@/types/api";
import { ChunkEditor } from "./chunk-editor";

interface ChunkViewerProps {
    projectId: string;
    chunks: BrdChunk[];
}

export function ChunkViewer({ projectId, chunks }: ChunkViewerProps) {
    const [localChunks, setLocalChunks] = React.useState(chunks);

    React.useEffect(() => {
        setLocalChunks(chunks);
    }, [chunks]);

    const handleUpdate = (updatedChunk: BrdChunk) => {
        setLocalChunks(prev => prev.map(c => c.id === updatedChunk.id ? updatedChunk : c));
    };

    if (!localChunks?.length) {
        return <div className="text-sm text-gray-500 italic p-4">No chunks generated yet.</div>;
    }

    return (
        <div className="flex flex-col gap-3">
            {localChunks.sort((a, b) => a.order_index - b.order_index).map((chunk) => (
                <ChunkEditor
                    key={chunk.id}
                    projectId={projectId}
                    chunk={chunk}
                    onSave={handleUpdate}
                />
            ))}
        </div>
    );
}
