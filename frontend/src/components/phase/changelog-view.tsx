import type { ConsolidationChangelog } from "@/types/api";

interface Props {
  changelog: ConsolidationChangelog;
}

export function ChangelogView({ changelog }: Props) {
  const hasContent =
    changelog.accepted.length > 0 ||
    changelog.rejected_with_reason.length > 0 ||
    changelog.additions_merged.length > 0 ||
    changelog.conflicts_for_user.length > 0;

  if (!hasContent) return null;

  return (
    <div className="rounded-lg border bg-white p-4">
      <h3 className="mb-3 font-semibold">Consolidation Changelog</h3>

      {changelog.accepted.length > 0 && (
        <div className="mb-3">
          <h4 className="text-sm font-medium text-green-700">
            Accepted ({changelog.accepted.length})
          </h4>
          <ul className="mt-1 space-y-1 text-sm">
            {changelog.accepted.map((item, i) => (
              <li key={i} className="rounded bg-green-50 px-3 py-1">
                <span className="font-medium">{String(item.from_agent ?? "")}:</span>{" "}
                {String(item.action_taken ?? item.comment_summary ?? JSON.stringify(item))}
              </li>
            ))}
          </ul>
        </div>
      )}

      {changelog.rejected_with_reason.length > 0 && (
        <div className="mb-3">
          <h4 className="text-sm font-medium text-red-700">
            Rejected ({changelog.rejected_with_reason.length})
          </h4>
          <ul className="mt-1 space-y-1 text-sm">
            {changelog.rejected_with_reason.map((item, i) => (
              <li key={i} className="rounded bg-red-50 px-3 py-1">
                <span className="font-medium">{String(item.from_agent ?? "")}:</span>{" "}
                {String(item.rejection_reason ?? JSON.stringify(item))}
              </li>
            ))}
          </ul>
        </div>
      )}

      {changelog.additions_merged.length > 0 && (
        <div className="mb-3">
          <h4 className="text-sm font-medium text-blue-700">
            Additions Merged ({changelog.additions_merged.length})
          </h4>
          <ul className="mt-1 space-y-1 text-sm">
            {changelog.additions_merged.map((item, i) => (
              <li key={i} className="rounded bg-blue-50 px-3 py-1">
                {String(item.description ?? JSON.stringify(item))}
              </li>
            ))}
          </ul>
        </div>
      )}

      {changelog.conflicts_for_user.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-yellow-700">
            Conflicts for User Decision ({changelog.conflicts_for_user.length})
          </h4>
          <ul className="mt-1 space-y-1 text-sm">
            {changelog.conflicts_for_user.map((item, i) => (
              <li key={i} className="rounded border border-yellow-300 bg-yellow-50 px-3 py-2">
                <p className="font-medium">{String(item.description ?? "")}</p>
                {Array.isArray(item.options) && (
                  <p className="mt-1 text-xs text-gray-600">
                    Options: {item.options.join(" | ")}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
