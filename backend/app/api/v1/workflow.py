"""Workflow endpoints — start pipeline, submit decisions, rollback."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.phase import (
    PipelineStatusResponse,
    RollbackRequest,
    StartPipelineRequest,
    UserDecisionRequest,
)
from app.services.pipeline_service import PipelineService

router = APIRouter()


@router.post("/{project_id}/pipeline/start")
async def start_pipeline(
    project_id: UUID,
    body: StartPipelineRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Start the multi-agent pipeline for a project."""
    svc = PipelineService(db)
    return await svc.start_pipeline(project_id)


@router.post("/{project_id}/pipeline/decide")
async def submit_decision(
    project_id: UUID,
    body: UserDecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit user approval or revision request for current phase."""
    svc = PipelineService(db)
    return await svc.submit_decision(
        project_id,
        decision=body.decision,
        feedback=body.feedback,
    )


@router.get("/{project_id}/pipeline/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get current pipeline execution status."""
    svc = PipelineService(db)
    result = await svc.get_pipeline_status(project_id)
    return PipelineStatusResponse(**result)


@router.post("/{project_id}/workflow/rollback")
async def rollback_workflow(
    project_id: UUID,
    body: RollbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """Rollback to a previous phase."""
    svc = PipelineService(db)
    return await svc.rollback_to_phase(project_id, body.target_phase)
