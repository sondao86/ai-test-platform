"""Project CRUD + file upload endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import FileTooLargeError
from app.dependencies import get_db
from app.schemas.project import (
    BrdChunkResponse,
    BrdChunkUpdate,
    BrdReuploadResponse,
    ExportRequest,
    ExportResponse,
    ProjectListResponse,
    ProjectResponse,
    RequirementResponse,
    RequirementUpdate,
    TestCaseCreate,
    TestCaseResponse,
    TestCaseUpdate,
    TestCategoryMapResponse,
    TestCategoryMapUpdate,
    WikiSyncRequest,
    WikiSyncResponse,
)
from app.schemas.project_config import (
    ProjectConfigResponse,
    ProjectConfigUpdate,
)
from app.services.export_service import ExportService
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    name: str = Form(...),
    description: str = Form(None),
    file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project, optionally uploading a BRD file."""
    svc = ProjectService(db)
    file_path = None
    file_name = None

    if file:
        content = await file.read()
        if len(content) > settings.max_upload_size_mb * 1024 * 1024:
            raise FileTooLargeError(settings.max_upload_size_mb)
        file_name = file.filename
        file_path = await svc.save_upload(content, file.filename)

    project = await svc.create_project(
        name=name,
        description=description,
        file_path=file_path,
        file_name=file_name,
    )
    return project


@router.get("", response_model=ProjectListResponse)
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects."""
    svc = ProjectService(db)
    projects, total = await svc.list_projects()
    return ProjectListResponse(items=projects, total=total)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get project details."""
    svc = ProjectService(db)
    return await svc.get_project(project_id)


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Archive a project."""
    svc = ProjectService(db)
    await svc.delete_project(project_id)


# --- Phase Artifact Endpoints ---


@router.get("/{project_id}/chunks", response_model=list[BrdChunkResponse])
async def get_chunks(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get Phase 1 output: BRD chunks."""
    svc = ProjectService(db)
    return await svc.get_chunks(project_id)


@router.put("/{project_id}/chunks/{chunk_id}", response_model=BrdChunkResponse)
async def update_chunk(
    project_id: UUID,
    chunk_id: UUID,
    body: BrdChunkUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Edit a BRD chunk."""
    svc = ProjectService(db)
    return await svc.update_chunk(chunk_id, **body.model_dump(exclude_unset=True))


@router.get("/{project_id}/requirements", response_model=list[RequirementResponse])
async def get_requirements(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get Phase 2 output: clarified requirements."""
    svc = ProjectService(db)
    return await svc.get_requirements(project_id)


@router.put("/{project_id}/requirements/{req_id}", response_model=RequirementResponse)
async def update_requirement(
    project_id: UUID,
    req_id: UUID,
    body: RequirementUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Edit a requirement."""
    svc = ProjectService(db)
    return await svc.update_requirement(req_id, **body.model_dump(exclude_unset=True))


@router.get("/{project_id}/classifications", response_model=list[TestCategoryMapResponse])
async def get_classifications(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get Phase 3 output: test category mappings."""
    svc = ProjectService(db)
    return await svc.get_classifications(project_id)


@router.put(
    "/{project_id}/classifications/{map_id}",
    response_model=TestCategoryMapResponse,
)
async def update_classification(
    project_id: UUID,
    map_id: UUID,
    body: TestCategoryMapUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Override a test category mapping."""
    svc = ProjectService(db)
    return await svc.update_classification(map_id, **body.model_dump(exclude_unset=True))


@router.get("/{project_id}/test-cases", response_model=list[TestCaseResponse])
async def get_test_cases(
    project_id: UUID,
    active_only: bool = Query(False, description="If true, return only active test cases"),
    db: AsyncSession = Depends(get_db),
):
    """Get Phase 4 output: test cases."""
    svc = ProjectService(db)
    return await svc.get_test_cases(project_id, active_only=active_only)


@router.put("/{project_id}/test-cases/{tc_id}", response_model=TestCaseResponse)
async def update_test_case(
    project_id: UUID,
    tc_id: UUID,
    body: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Edit a test case."""
    svc = ProjectService(db)
    return await svc.update_test_case(tc_id, **body.model_dump(exclude_unset=True))


# --- Manual test case creation ---


@router.post("/{project_id}/test-cases", response_model=TestCaseResponse, status_code=201)
async def create_test_case(
    project_id: UUID,
    body: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a test case manually."""
    svc = ProjectService(db)
    return await svc.create_test_case(project_id, **body.model_dump())


# --- Test case activate / deactivate ---


@router.post("/{project_id}/test-cases/{tc_id}/deactivate", response_model=TestCaseResponse)
async def deactivate_test_case(
    project_id: UUID,
    tc_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a test case (excluded from future executions)."""
    svc = ProjectService(db)
    return await svc.deactivate_test_case(tc_id)


@router.post("/{project_id}/test-cases/{tc_id}/activate", response_model=TestCaseResponse)
async def activate_test_case(
    project_id: UUID,
    tc_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Re-activate a deactivated test case."""
    svc = ProjectService(db)
    return await svc.activate_test_case(tc_id)


# --- Export ---


@router.post("/{project_id}/test-cases/export")
async def export_test_cases(
    project_id: UUID,
    body: ExportRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Export test cases as a hybrid domain-first folder structure ZIP."""
    svc = ExportService(db)
    output_dir = body.output_dir if body else None
    result = await svc.export_test_cases(project_id, output_dir=output_dir)
    export_path = result["export_path"]
    return FileResponse(
        path=export_path,
        media_type="application/zip",
        filename=export_path.rsplit("/", 1)[-1],
        headers={
            "X-Export-Project-Id": result["project_id"],
            "X-Export-Total-Tests": str(result["total_tests"]),
            "X-Export-Domains": ",".join(result["domains"]),
        },
    )


# --- BRD re-upload ---


@router.post("/{project_id}/brd", response_model=BrdReuploadResponse)
async def reupload_brd(
    project_id: UUID,
    file: UploadFile = File(...),
    discard_artifacts: bool = Form(True),
    db: AsyncSession = Depends(get_db),
):
    """Re-upload a BRD file for an existing project."""
    svc = ProjectService(db)
    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise FileTooLargeError(settings.max_upload_size_mb)

    file_path = await svc.save_upload(content, file.filename)
    project = await svc.reupload_brd(
        project_id,
        file_path=file_path,
        file_name=file.filename,
        discard_artifacts=discard_artifacts,
    )
    return BrdReuploadResponse(
        project_id=project.id,
        brd_version=project.brd_version,
        file_name=project.file_name,
        artifacts_discarded=discard_artifacts,
        message=f"BRD re-uploaded (version {project.brd_version})."
        + (" Pipeline artifacts discarded." if discard_artifacts else ""),
    )


# --- Wiki sync ---


@router.post("/{project_id}/brd/sync-wiki", response_model=WikiSyncResponse)
async def sync_wiki_brd(
    project_id: UUID,
    body: WikiSyncRequest,
    db: AsyncSession = Depends(get_db),
):
    """Sync BRD content from Azure DevOps Wiki."""
    svc = ProjectService(db)
    project = await svc.sync_wiki_brd(
        project_id,
        page_path=body.page_path,
        discard_artifacts=body.discard_artifacts,
    )
    return WikiSyncResponse(
        project_id=project.id,
        brd_version=project.brd_version,
        brd_source="wiki_sync",
        page_path=body.page_path,
        content_length=len(project.raw_text) if project.raw_text else 0,
        artifacts_discarded=body.discard_artifacts,
        message=f"Wiki synced (version {project.brd_version})."
        + (" Pipeline artifacts discarded." if body.discard_artifacts else ""),
    )


# --- Project config ---


@router.get("/{project_id}/config", response_model=ProjectConfigResponse | None)
async def get_project_config(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get saved environment config for a project."""
    svc = ProjectService(db)
    config = await svc.get_project_config(project_id)
    if config is None:
        return None
    return ProjectConfigResponse.from_model(config)


@router.put("/{project_id}/config", response_model=ProjectConfigResponse)
async def upsert_project_config(
    project_id: UUID,
    body: ProjectConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Save or update environment config for a project."""
    svc = ProjectService(db)
    config = await svc.upsert_project_config(project_id, **body.model_dump(exclude_unset=True))
    return ProjectConfigResponse.from_model(config)
