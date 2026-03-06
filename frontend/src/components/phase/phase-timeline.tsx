import { cn } from "@/lib/utils";
import { PHASE_NAMES, PHASE_DESCRIPTIONS } from "@/lib/utils";

interface Props {
  currentPhase: number;
  status: string;
  selectedPhase: number | null;
  onSelectPhase: (phase: number) => void;
}

export function PhaseTimeline({ currentPhase, status, selectedPhase, onSelectPhase }: Props) {
  return (
    <div className="flex gap-2">
      {[1, 2, 3, 4].map((phase) => {
        const isCompleted = phase < currentPhase;
        const isCurrent = phase === currentPhase;
        const isSelected = phase === selectedPhase;

        return (
          <button
            key={phase}
            onClick={() => onSelectPhase(phase)}
            className={cn(
              "flex-1 rounded-lg border p-4 text-left transition-colors",
              isSelected && "ring-2 ring-blue-500",
              isCompleted && "border-green-300 bg-green-50",
              isCurrent && "border-blue-300 bg-blue-50",
              !isCompleted && !isCurrent && "border-gray-200 bg-white opacity-50"
            )}
          >
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold",
                  isCompleted && "bg-green-600 text-white",
                  isCurrent && "bg-blue-600 text-white",
                  !isCompleted && !isCurrent && "bg-gray-300 text-gray-600"
                )}
              >
                {isCompleted ? "\u2713" : phase}
              </span>
              <span className="text-sm font-medium">{PHASE_NAMES[phase]}</span>
            </div>
            <p className="mt-1 text-xs text-gray-500">{PHASE_DESCRIPTIONS[phase]}</p>
            {isCurrent && (
              <span className="mt-2 inline-block rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700">
                {status === "awaiting_user" ? "Awaiting Review" : "In Progress"}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
