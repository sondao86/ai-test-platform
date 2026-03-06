"use client";

import * as React from "react";
import type { AgentReview, AgentComment } from "@/types/api";
import { AGENT_COLORS, SEVERITY_COLORS } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible";
import { Check, X, ChevronDown, Filter } from "lucide-react";
import { AgentAvatar } from "./agent-avatar";
import { ReviewDiffView } from "./review-diff-view";

interface Props {
  review: AgentReview;
  onAcceptComment?: (comment: AgentComment) => void;
  onRejectComment?: (comment: AgentComment) => void;
}

export function AgentReviewCard({ review, onAcceptComment, onRejectComment }: Props) {
  const agentColorClass = AGENT_COLORS[review.agent_id] || "bg-gray-100 text-gray-800 border-gray-200";
  const [showOnlyCritical, setShowOnlyCritical] = React.useState(false);

  const comments = review.comments || [];
  const filteredComments = showOnlyCritical
    ? comments.filter(c => c.severity === "critical")
    : comments;

  const initialVisibleCount = 2;
  const hasMoreComments = filteredComments.length > initialVisibleCount;

  return (
    <div className={`rounded-lg border bg-white shadow-sm overflow-hidden ${agentColorClass.replace('bg-', 'border-').split(' ')[0]} border-opacity-50`}>
      {/* Agent Header */}
      <div className={`flex items-center justify-between p-4 border-b border-gray-100 ${agentColorClass.split(' ')[0].replace('100', '50')}`}>
        <div className="flex items-center gap-3">
          <AgentAvatar agentId={review.agent_id} size="lg" />
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-900">{review.agent_name}</span>
              <span className="rounded-full bg-gray-200 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-gray-600">
                {review.role}
              </span>
            </div>
            {review.confidence !== null && (
              <div className="text-xs text-gray-500 mt-0.5">
                Confidence: {Math.round(review.confidence * 100)}%
              </div>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <StatusBadge status={review.status} />
          {comments.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-xs px-2 text-gray-500"
              onClick={() => setShowOnlyCritical(!showOnlyCritical)}
            >
              <Filter className="h-3 w-3 mr-1" />
              {showOnlyCritical ? "Show All" : "Critical Only"}
            </Button>
          )}
        </div>
      </div>

      {/* Comments */}
      {filteredComments.length > 0 ? (
        <div className="p-4">
          <Collapsible>
            <div className="space-y-3">
              {filteredComments.slice(0, initialVisibleCount).map((comment, i) => (
                <CommentItem
                  key={i}
                  comment={comment}
                  onAccept={() => onAcceptComment?.(comment)}
                  onReject={() => onRejectComment?.(comment)}
                />
              ))}

              <CollapsibleContent className="space-y-3 mt-3">
                {filteredComments.slice(initialVisibleCount).map((comment, i) => (
                  <CommentItem
                    key={i + initialVisibleCount}
                    comment={comment}
                    onAccept={() => onAcceptComment?.(comment)}
                    onReject={() => onRejectComment?.(comment)}
                  />
                ))}
              </CollapsibleContent>
            </div>

            {hasMoreComments && (
              <CollapsibleTrigger asChild>
                <Button variant="ghost" size="sm" className="w-full mt-2 text-xs text-gray-500">
                  <span className="flex items-center">
                    Show {filteredComments.length - initialVisibleCount} more comments <ChevronDown className="h-3 w-3 ml-1" />
                  </span>
                </Button>
              </CollapsibleTrigger>
            )}
          </Collapsible>
        </div>
      ) : (
        <div className="p-4 text-sm text-gray-500 italic">
          No {showOnlyCritical ? "critical " : ""}comments provided.
        </div>
      )}

      {/* Additions */}
      {review.additions && review.additions.length > 0 && (
        <div className="bg-gray-50 p-3 text-xs font-medium text-gray-600 border-t border-gray-100 flex items-center justify-between">
          <span>+{review.additions.length} new items suggested</span>
          <Button variant="outline" size="sm" className="h-6 text-[10px]">View Additions</Button>
        </div>
      )}
    </div>
  );
}

function CommentItem({ comment, onAccept, onReject }: { comment: AgentComment, onAccept: () => void, onReject: () => void }) {
  const sevClasses = SEVERITY_COLORS[comment.severity] || "bg-gray-50 border-gray-200 text-gray-800";

  return (
    <div className={`rounded-md border p-3 ${sevClasses} bg-opacity-30`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className={`text-[10px] h-5 uppercase border-current ${sevClasses.split(' ')[1]}`}>
              {comment.severity}
            </Badge>
            {comment.target_id && (
              <code className="text-[10px] bg-white/50 px-1.5 py-0.5 rounded text-gray-600">
                @{comment.target_id}
              </code>
            )}
          </div>
          <p className="text-sm font-medium mt-1 leading-snug">{comment.comment}</p>

          {comment.proposed_change && (
            <ReviewDiffView
              originalText="/* Original text context not provided. In real app, fetch from target_id */"
              proposedText={comment.proposed_change}
            />
          )}
        </div>

        <div className="flex flex-col gap-1 shrink-0">
          <Button variant="outline" size="sm" className="h-6 w-6 p-0 bg-white hover:bg-green-50 hover:text-green-600 border-green-200" onClick={onAccept} title="Accept Suggestion">
            <Check className="h-3 w-3 text-green-600" />
          </Button>
          <Button variant="outline" size="sm" className="h-6 w-6 p-0 bg-white hover:bg-red-50 hover:text-red-600 border-red-200" onClick={onReject} title="Reject Suggestion">
            <X className="h-3 w-3 text-red-600" />
          </Button>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    approved: "bg-green-100 text-green-800 border-green-200",
    changes_requested: "bg-yellow-100 text-yellow-800 border-yellow-200",
    additions_suggested: "bg-blue-100 text-blue-800 border-blue-200",
    consolidated: "bg-purple-100 text-purple-800 border-purple-200",
  };

  return (
    <Badge variant="outline" className={`text-xs border ${colors[status] || "bg-gray-100 border-gray-200"}`}>
      {status.replace(/_/g, " ")}
    </Badge>
  );
}
