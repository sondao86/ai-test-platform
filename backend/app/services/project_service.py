"""Project service — CRUD operations for projects and their artifacts."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    PipelineAlreadyRunningError,
    ProjectNotFoundError,
    TestCaseNotFoundError,
    WikiConfigMissingError,
    WikiSyncFailedError,
)
from app.models.agent_review import AgentReview
from app.models.brd_chunk import BrdChunk
from app.models.clarification import Clarification
from app.models.phase_history import PhaseHistory
from app.models.project import Project
from app.models.project_config import ProjectConfig
from app.models.requirement import Requirement
from app.models.test_case import TestCase
from app.models.test_category_map import TestCategoryMap
from app.services.document_parser import parse_document

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(
        self,
        name: str,
        description: str | None = None,
        file_path: str | None = None,
        file_name: str | None = None,
    ) -> Project:
        raw_text = None
        if file_path:
            raw_text = parse_document(file_path)

        project = Project(
            name=name,
            description=description,
            file_path=file_path,
            file_name=file_name,
            raw_text=raw_text,
            status="created",
            current_phase=0,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        logger.info("Created project: %s (%s)", project.name, project.id)
        return project

    async def get_project(self, project_id: uuid.UUID) -> Project:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            raise ProjectNotFoundError(str(project_id))
        return project

    async def list_projects(self) -> tuple[list[Project], int]:
        result = await self.db.execute(select(Project).order_by(Project.created_at.desc()))
        projects = list(result.scalars().all())
        count_result = await self.db.execute(select(func.count(Project.id)))
        total = count_result.scalar() or 0
        return projects, total

    async def delete_project(self, project_id: uuid.UUID) -> None:
        project = await self.get_project(project_id)
        project.status = "archived"
        await self.db.commit()

    async def update_project_phase(self, project_id: uuid.UUID, phase: int, status: str) -> Project:
        project = await self.get_project(project_id)
        project.current_phase = phase
        project.status = status
        await self.db.commit()
        await self.db.refresh(project)
        return project

    # --- Artifact queries ---

    async def get_chunks(self, project_id: uuid.UUID) -> list[BrdChunk]:
        result = await self.db.execute(
            select(BrdChunk)
            .where(BrdChunk.project_id == project_id)
            .order_by(BrdChunk.order_index)
        )
        return list(result.scalars().all())

    async def update_chunk(self, chunk_id: uuid.UUID, **kwargs) -> BrdChunk:
        result = await self.db.execute(select(BrdChunk).where(BrdChunk.id == chunk_id))
        chunk = result.scalar_one_or_none()
        if not chunk:
            raise ProjectNotFoundError(str(chunk_id))
        for key, value in kwargs.items():
            if value is not None:
                setattr(chunk, key, value)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def get_requirements(self, project_id: uuid.UUID) -> list[Requirement]:
        result = await self.db.execute(
            select(Requirement).where(Requirement.project_id == project_id)
        )
        return list(result.scalars().all())

    async def update_requirement(self, req_id: uuid.UUID, **kwargs) -> Requirement:
        result = await self.db.execute(select(Requirement).where(Requirement.id == req_id))
        req = result.scalar_one_or_none()
        if not req:
            raise ProjectNotFoundError(str(req_id))
        for key, value in kwargs.items():
            if value is not None:
                setattr(req, key, value)
        await self.db.commit()
        await self.db.refresh(req)
        return req

    async def get_classifications(self, project_id: uuid.UUID) -> list[TestCategoryMap]:
        result = await self.db.execute(
            select(TestCategoryMap).where(TestCategoryMap.project_id == project_id)
        )
        return list(result.scalars().all())

    async def update_classification(self, map_id: uuid.UUID, **kwargs) -> TestCategoryMap:
        result = await self.db.execute(
            select(TestCategoryMap).where(TestCategoryMap.id == map_id)
        )
        tcm = result.scalar_one_or_none()
        if not tcm:
            raise ProjectNotFoundError(str(map_id))
        for key, value in kwargs.items():
            if value is not None:
                setattr(tcm, key, value)
        await self.db.commit()
        await self.db.refresh(tcm)
        return tcm

    async def get_test_cases(
        self, project_id: uuid.UUID, active_only: bool = False
    ) -> list[TestCase]:
        query = select(TestCase).where(TestCase.project_id == project_id)
        if active_only:
            query = query.where(TestCase.is_active == True)  # noqa: E712
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_test_case(self, tc_id: uuid.UUID, **kwargs) -> TestCase:
        result = await self.db.execute(select(TestCase).where(TestCase.id == tc_id))
        tc = result.scalar_one_or_none()
        if not tc:
            raise ProjectNotFoundError(str(tc_id))
        for key, value in kwargs.items():
            if value is not None:
                setattr(tc, key, value)
        await self.db.commit()
        await self.db.refresh(tc)
        return tc

    # --- Reviews & history ---

    async def get_phase_reviews(
        self, project_id: uuid.UUID, phase_id: int
    ) -> list[AgentReview]:
        result = await self.db.execute(
            select(AgentReview)
            .where(AgentReview.project_id == project_id, AgentReview.phase_id == phase_id)
            .order_by(AgentReview.created_at)
        )
        return list(result.scalars().all())

    async def save_agent_review(self, **kwargs) -> AgentReview:
        review = AgentReview(**kwargs)
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_workflow_history(self, project_id: uuid.UUID) -> list[PhaseHistory]:
        result = await self.db.execute(
            select(PhaseHistory)
            .where(PhaseHistory.project_id == project_id)
            .order_by(PhaseHistory.created_at)
        )
        return list(result.scalars().all())

    async def add_phase_history(self, **kwargs) -> PhaseHistory:
        entry = PhaseHistory(**kwargs)
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def save_upload(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return file path."""
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(filename).suffix
        dest = upload_dir / f"{uuid.uuid4()}{ext}"
        dest.write_bytes(file_content)
        logger.info("Saved upload: %s → %s", filename, dest)
        return str(dest)

    # --- Test case management ---

    async def create_test_case(self, project_id: uuid.UUID, **kwargs) -> TestCase:
        """Create a manual test case."""
        await self.get_project(project_id)  # ensure project exists
        tc = TestCase(
            project_id=project_id,
            source="manual",
            **kwargs,
        )
        self.db.add(tc)
        await self.db.commit()
        await self.db.refresh(tc)
        logger.info("Created manual test case %s for project %s", tc.test_id, project_id)
        return tc

    async def deactivate_test_case(self, tc_id: uuid.UUID) -> TestCase:
        result = await self.db.execute(select(TestCase).where(TestCase.id == tc_id))
        tc = result.scalar_one_or_none()
        if not tc:
            raise TestCaseNotFoundError(str(tc_id))
        tc.is_active = False
        await self.db.commit()
        await self.db.refresh(tc)
        return tc

    async def activate_test_case(self, tc_id: uuid.UUID) -> TestCase:
        result = await self.db.execute(select(TestCase).where(TestCase.id == tc_id))
        tc = result.scalar_one_or_none()
        if not tc:
            raise TestCaseNotFoundError(str(tc_id))
        tc.is_active = True
        await self.db.commit()
        await self.db.refresh(tc)
        return tc

    # --- Project config ---

    async def get_project_config(self, project_id: uuid.UUID) -> ProjectConfig | None:
        await self.get_project(project_id)  # ensure project exists
        result = await self.db.execute(
            select(ProjectConfig).where(ProjectConfig.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def upsert_project_config(
        self, project_id: uuid.UUID, **kwargs
    ) -> ProjectConfig:
        await self.get_project(project_id)  # ensure project exists
        result = await self.db.execute(
            select(ProjectConfig).where(ProjectConfig.project_id == project_id)
        )
        config = result.scalar_one_or_none()
        if config:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(config, key, value)
        else:
            config = ProjectConfig(project_id=project_id, **kwargs)
            self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    # --- BRD re-upload ---

    async def reupload_brd(
        self,
        project_id: uuid.UUID,
        file_path: str,
        file_name: str,
        discard_artifacts: bool = True,
    ) -> Project:
        """Re-upload a BRD file for an existing project."""
        # Import here to avoid circular dependency
        from app.services.pipeline_service import _active_runs

        project = await self.get_project(project_id)
        pid = str(project_id)

        # Guard: reject if pipeline is currently running
        if pid in _active_runs and _active_runs[pid].get("status") == "running":
            raise PipelineAlreadyRunningError(pid)

        # Parse new document
        raw_text = parse_document(file_path)

        # Update project fields
        project.raw_text = raw_text
        project.file_path = file_path
        project.file_name = file_name
        project.brd_version += 1

        if discard_artifacts:
            await self._discard_pipeline_artifacts(project_id)
            project.current_phase = 0
            project.status = "created"

        # Record history
        await self.add_phase_history(
            project_id=project_id,
            phase_id=project.current_phase,
            phase_name="BRD Re-upload",
            action="brd_reuploaded",
            snapshot={
                "brd_version": project.brd_version,
                "discard_artifacts": discard_artifacts,
                "file_name": file_name,
            },
        )

        await self.db.commit()
        await self.db.refresh(project)
        logger.info(
            "Re-uploaded BRD for project %s (version %d, discard=%s)",
            project_id, project.brd_version, discard_artifacts,
        )
        return project

    async def sync_wiki_brd(
        self,
        project_id: uuid.UUID,
        page_path: str | None = None,
        discard_artifacts: bool = True,
    ) -> Project:
        """Sync BRD content from Azure DevOps Wiki."""
        from app.services.pipeline_service import _active_runs
        from app.services.wiki_sync_service import WikiSyncService

        project = await self.get_project(project_id)
        pid = str(project_id)

        # Guard: reject if pipeline is currently running
        if pid in _active_runs and _active_runs[pid].get("status") == "running":
            raise PipelineAlreadyRunningError(pid)

        # Validate wiki config
        config = await self.get_project_config(project_id)
        if (
            not config
            or not config.azure_wiki_org
            or not config.azure_wiki_project
            or not config.azure_wiki_pat
        ):
            raise WikiConfigMissingError(pid)

        # Sync from wiki
        wiki_svc = WikiSyncService(
            organization=config.azure_wiki_org,
            project=config.azure_wiki_project,
            wiki_name=config.azure_wiki_name,
            pat=config.azure_wiki_pat,
        )
        try:
            raw_text = await wiki_svc.sync_page(page_path)
        except RuntimeError as exc:
            raise WikiSyncFailedError(pid, str(exc))

        # Update project
        project.raw_text = raw_text
        project.brd_version += 1
        project.brd_source = "wiki_sync"
        project.file_name = page_path or "wiki_full_sync"
        project.file_path = None

        if discard_artifacts:
            await self._discard_pipeline_artifacts(project_id)
            project.current_phase = 0
            project.status = "created"

        # Record history
        await self.add_phase_history(
            project_id=project_id,
            phase_id=project.current_phase,
            phase_name="Wiki Sync",
            action="wiki_synced",
            snapshot={
                "brd_version": project.brd_version,
                "brd_source": "wiki_sync",
                "page_path": page_path,
                "content_length": len(raw_text),
                "discard_artifacts": discard_artifacts,
            },
        )

        await self.db.commit()
        await self.db.refresh(project)
        logger.info(
            "Wiki-synced BRD for project %s (version %d, page=%s)",
            project_id, project.brd_version, page_path or "all",
        )
        return project

    async def _discard_pipeline_artifacts(self, project_id: uuid.UUID) -> None:
        """Delete all pipeline-generated artifacts, preserving manual test cases."""
        await self.db.execute(
            delete(BrdChunk).where(BrdChunk.project_id == project_id)
        )
        await self.db.execute(
            delete(Clarification).where(Clarification.project_id == project_id)
        )
        await self.db.execute(
            delete(Requirement).where(Requirement.project_id == project_id)
        )
        await self.db.execute(
            delete(TestCategoryMap).where(TestCategoryMap.project_id == project_id)
        )
        # Only delete pipeline-generated test cases; keep manual ones
        await self.db.execute(
            delete(TestCase).where(
                TestCase.project_id == project_id,
                TestCase.source == "pipeline",
            )
        )
        await self.db.flush()
        logger.info("Discarded pipeline artifacts for project %s", project_id)
