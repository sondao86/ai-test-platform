import type { PhaseResult } from "@/types/api";
import { AgentReviewCard } from "@/components/agent/agent-review-card";
import { ChangelogView } from "@/components/phase/changelog-view";

interface Props {
  result: PhaseResult;
}

export function PhaseDetail({ result }: Props) {
  const reviewerReviews = result.reviews.filter((r) => r.role === "reviewer");

  return (
    <div className="space-y-6">
      {/* Phase Header */}
      <div className="rounded-lg border bg-white p-4">
        <h2 className="text-lg font-semibold">
          Phase {result.phase_id}: {result.phase_name}
        </h2>
        <div className="mt-2 flex gap-4 text-sm text-gray-600">
          <span>Status: <strong>{result.status}</strong></span>
          <span>Primary: <strong>{result.primary_agent}</strong></span>
          <span>Revision: <strong>#{result.revision_round}</strong></span>
        </div>
      </div>

      {/* Consolidated Output */}
      {result.consolidated_output && (
        <div className="rounded-lg border bg-white p-4">
          <h3 className="mb-2 font-semibold">Consolidated Output</h3>
          <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
            {JSON.stringify(result.consolidated_output, null, 2)}
          </pre>
        </div>
      )}

      {/* Agent Reviews */}
      {reviewerReviews.length > 0 && (
        <div>
          <h3 className="mb-3 font-semibold">
            Agent Reviews ({reviewerReviews.length})
          </h3>
          <div className="grid gap-4 lg:grid-cols-2">
            {reviewerReviews.map((review) => (
              <AgentReviewCard key={review.id} review={review} />
            ))}
          </div>
        </div>
      )}

      {/* Changelog */}
      {result.changelog && (
        <ChangelogView changelog={result.changelog} />
      )}
    </div>
  );
}
