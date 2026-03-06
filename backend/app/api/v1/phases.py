"""Phase results + agent reviews endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.graph.phase_config import get_phase_config
from app.schemas.phase import AgentReviewResponse, PhaseHistoryResponse, PhaseResultResponse
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/{project_id}/phases/{phase_id}", response_model=PhaseResultResponse)
async def get_phase_result(
    project_id: UUID,
    phase_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get phase result: consolidated output + reviews + changelog."""
    svc = ProjectService(db)
    config = get_phase_config(phase_id)
    reviews = await svc.get_phase_reviews(project_id, phase_id)

    # Find primary and reviewer entries
    primary_review = None
    reviewer_reviews = []
    for r in reviews:
        if r.role == "primary":
            primary_review = r
        else:
            reviewer_reviews.append(r)

    return PhaseResultResponse(
        phase_id=phase_id,
        phase_name=config.phase_name,
        status="completed" if reviews else "pending",
        primary_agent=config.primary_agent_id,
        reviewer_agents=config.reviewer_agent_ids,
        consolidated_output=primary_review.consolidation_summary if primary_review else None,
        reviews=[AgentReviewResponse.model_validate(r) for r in reviews],
        changelog=primary_review.consolidation_summary if primary_review else None,
        revision_round=max((r.revision_round for r in reviews), default=1),
    )


@router.get(
    "/{project_id}/phases/{phase_id}/reviews",
    response_model=list[AgentReviewResponse],
)
async def get_phase_reviews(
    project_id: UUID,
    phase_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all agent reviews for a specific phase."""
    svc = ProjectService(db)
    reviews = await svc.get_phase_reviews(project_id, phase_id)
    return [AgentReviewResponse.model_validate(r) for r in reviews]


@router.get(
    "/{project_id}/workflow/history",
    response_model=list[PhaseHistoryResponse],
)
async def get_workflow_history(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get full workflow audit log."""
    svc = ProjectService(db)
    history = await svc.get_workflow_history(project_id)
    return [PhaseHistoryResponse.model_validate(h) for h in history]
