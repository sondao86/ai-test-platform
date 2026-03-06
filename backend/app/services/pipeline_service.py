"""Pipeline service — manages graph execution, resume, and persistence."""

from __future__ import annotations

import logging
import uuid
from dataclasses import asdict

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PHASE_NUMBER_TO_ENUM
from app.core.exceptions import (
    InvalidPhaseTransitionError,
    PipelineAlreadyRunningError,
)
from app.graph.outer_graph import compile_pipeline_graph
from app.graph.phase_config import get_phase_config
from app.graph.state import PipelineState
from app.models.agent_review import AgentReview as AgentReviewModel
from app.models.brd_chunk import BrdChunk
from app.models.clarification import Clarification
from app.models.phase_history import PhaseHistory
from app.models.requirement import Requirement
from app.models.test_case import TestCase
from app.models.test_category_map import TestCategoryMap
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)

# In-memory store for active pipeline runs (production would use langgraph-checkpoint-postgres)
_active_runs: dict[str, dict] = {}


class PipelineService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_service = ProjectService(db)

    async def start_pipeline(self, project_id: uuid.UUID) -> dict:
        """Start the pipeline for a project."""
        pid = str(project_id)
        if pid in _active_runs and _active_runs[pid].get("status") == "running":
            raise PipelineAlreadyRunningError(pid)

        project = await self.project_service.get_project(project_id)

        if not project.raw_text:
            raise ValueError("Project has no document text. Upload a BRD file first.")

        # Initialize pipeline state
        initial_state: PipelineState = {
            "project_id": pid,
            "current_phase": 1,
            "raw_document": project.raw_text,
            "document_metadata": {"file_name": project.file_name},
            "brd_chunks": None,
            "clarified_requirements": None,
            "test_category_map": None,
            "test_case_specs": None,
            "current_step": "primary_generate",
            "current_primary_output": None,
            "current_reviews": [],
            "current_consolidated_output": None,
            "current_consolidation_summary": None,
            "user_decision": None,
            "user_feedback": None,
            "phase_results": [],
            "revision_round": 1,
        }

        # Update project status
        await self.project_service.update_project_phase(project_id, 1, "in_progress")

        # Record history
        await self.project_service.add_phase_history(
            project_id=project_id,
            phase_id=1,
            phase_name="Ingest & Chunk",
            action="pipeline_started",
        )

        # Compile and run graph
        graph = compile_pipeline_graph()

        _active_runs[pid] = {
            "status": "running",
            "graph": graph,
            "state": initial_state,
            "thread_id": pid,
        }

        try:
            # Run until first interrupt (human_gate)
            result = await graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": pid}},
            )

            _active_runs[pid]["state"] = result
            _active_runs[pid]["status"] = "awaiting_user"

            # Persist phase artifacts after completion
            await self._persist_phase_artifacts(project_id, result)

            return {
                "project_id": pid,
                "status": "awaiting_user",
                "current_phase": result.get("current_phase", 1),
                "message": "Pipeline started. Review phase output and approve or revise.",
            }
        except Exception as e:
            _active_runs[pid]["status"] = "error"
            logger.exception("Pipeline error for project %s", pid)
            raise

    async def submit_decision(
        self,
        project_id: uuid.UUID,
        decision: str,
        feedback: str | None = None,
    ) -> dict:
        """Submit user decision (approve/revise) for the current phase."""
        pid = str(project_id)
        run = _active_runs.get(pid)

        if not run:
            raise ValueError(f"No active pipeline run for project {pid}")

        graph = run["graph"]
        current_state = run["state"]
        current_phase = current_state.get("current_phase", 1)

        # Record user decision
        await self.project_service.add_phase_history(
            project_id=project_id,
            phase_id=current_phase,
            phase_name=get_phase_config(current_phase).phase_name,
            action=f"user_{decision}",
            user_decision=decision,
            user_feedback=feedback,
            revision_round=current_state.get("revision_round", 1),
        )

        if decision == "approved":
            # Save agent reviews to DB
            await self._persist_reviews(project_id, current_state)
            await self.project_service.update_project_phase(
                project_id, current_phase, "in_progress"
            )

        # Resume graph with user's decision
        user_input = {"decision": decision, "feedback": feedback}

        run["status"] = "running"
        try:
            result = await graph.ainvoke(
                None,  # Resume from interrupt
                config={"configurable": {"thread_id": pid}},
            )

            run["state"] = result
            run["status"] = "awaiting_user" if result.get("user_decision") is None else "completed"

            await self._persist_phase_artifacts(project_id, result)

            return {
                "project_id": pid,
                "status": run["status"],
                "current_phase": result.get("current_phase", current_phase),
                "message": "Decision processed.",
            }
        except Exception as e:
            run["status"] = "error"
            logger.exception("Pipeline error during decision for project %s", pid)
            raise

    async def get_pipeline_status(self, project_id: uuid.UUID) -> dict:
        """Get current pipeline status."""
        pid = str(project_id)
        run = _active_runs.get(pid)

        if not run:
            project = await self.project_service.get_project(project_id)
            return {
                "project_id": pid,
                "current_phase": project.current_phase,
                "current_step": "idle",
                "phase_name": PHASE_NUMBER_TO_ENUM.get(project.current_phase, "none"),
                "status": project.status,
            }

        state = run["state"]
        phase_id = state.get("current_phase", 0)
        return {
            "project_id": pid,
            "current_phase": phase_id,
            "current_step": state.get("current_step", "unknown"),
            "phase_name": get_phase_config(phase_id).phase_name if phase_id > 0 else "none",
            "status": run["status"],
        }

    async def rollback_to_phase(self, project_id: uuid.UUID, target_phase: int) -> dict:
        """Rollback pipeline to a previous phase."""
        project = await self.project_service.get_project(project_id)

        if target_phase >= project.current_phase:
            raise InvalidPhaseTransitionError(project.current_phase, target_phase)

        await self.project_service.add_phase_history(
            project_id=project_id,
            phase_id=project.current_phase,
            phase_name=get_phase_config(project.current_phase).phase_name,
            action=f"rollback_to_phase_{target_phase}",
        )

        await self.project_service.update_project_phase(
            project_id, target_phase, "in_progress"
        )

        # Clear active run
        pid = str(project_id)
        _active_runs.pop(pid, None)

        return {
            "project_id": pid,
            "rolled_back_to": target_phase,
            "message": f"Rolled back to phase {target_phase}. Restart the pipeline to continue.",
        }

    # --- Persistence helpers ---

    async def _persist_phase_artifacts(
        self, project_id: uuid.UUID, state: dict
    ) -> None:
        """Persist phase artifacts from graph state to database.

        Uses delete-before-insert to avoid duplicate accumulation on re-runs.
        Manual test cases (source='manual') are preserved.
        """
        # Persist BRD chunks (delete old → insert new)
        brd_chunks = state.get("brd_chunks")
        if brd_chunks and isinstance(brd_chunks, list):
            await self.db.execute(
                delete(BrdChunk).where(BrdChunk.project_id == project_id)
            )
            for i, chunk in enumerate(brd_chunks):
                if isinstance(chunk, dict):
                    self.db.add(BrdChunk(
                        project_id=project_id,
                        section_title=chunk.get("section_title", f"Section {i}"),
                        section_type=chunk.get("section_type", "other"),
                        content=chunk.get("content", ""),
                        order_index=chunk.get("order_index", i),
                        metadata_=chunk.get("metadata", {}),
                        cross_references=chunk.get("cross_references", []),
                    ))

        # Persist requirements (delete old → insert new)
        requirements = state.get("clarified_requirements")
        if requirements and isinstance(requirements, list):
            await self.db.execute(
                delete(Requirement).where(Requirement.project_id == project_id)
            )
            for req in requirements:
                if isinstance(req, dict):
                    self.db.add(Requirement(
                        project_id=project_id,
                        requirement_id=req.get("requirement_id", "REQ-???"),
                        title=req.get("title", "Untitled"),
                        description=req.get("description", ""),
                        priority=req.get("priority", "medium"),
                        business_rules=req.get("business_rules", []),
                        kpis=req.get("kpis", []),
                        data_elements=req.get("data_elements", []),
                    ))

        # Persist test category mappings (delete old → insert new)
        tcm = state.get("test_category_map")
        if tcm and isinstance(tcm, list):
            await self.db.execute(
                delete(TestCategoryMap).where(TestCategoryMap.project_id == project_id)
            )
            for mapping in tcm:
                if isinstance(mapping, dict):
                    self.db.add(TestCategoryMap(
                        project_id=project_id,
                        test_category=mapping.get("test_category", ""),
                        sub_category=mapping.get("sub_category"),
                        rationale=mapping.get("rationale", ""),
                        confidence=mapping.get("confidence", 0.0),
                        pipeline_layer=mapping.get("pipeline_layer"),
                        tool_suggestion=mapping.get("tool_suggestion"),
                        domain=mapping.get("domain"),
                    ))

        # Persist test cases (delete old pipeline-generated → insert new; keep manual)
        test_cases = state.get("test_case_specs")
        if test_cases and isinstance(test_cases, list):
            await self.db.execute(
                delete(TestCase).where(
                    TestCase.project_id == project_id,
                    TestCase.source == "pipeline",
                )
            )
            for tc in test_cases:
                if isinstance(tc, dict):
                    self.db.add(TestCase(
                        project_id=project_id,
                        test_id=tc.get("test_id", "TC-???"),
                        title=tc.get("title", "Untitled"),
                        description=tc.get("description", ""),
                        test_category=tc.get("test_category", ""),
                        pipeline_layer=tc.get("pipeline_layer", "bronze"),
                        tool=tc.get("tool", "custom_sql"),
                        sql_logic=tc.get("sql_logic"),
                        dbt_test_yaml=tc.get("dbt_test_yaml"),
                        great_expectations_config=tc.get("great_expectations_config"),
                        input_data=tc.get("input_data"),
                        expected_result=tc.get("expected_result"),
                        severity=tc.get("severity", "medium"),
                        priority=tc.get("priority", 3),
                        sla_seconds=tc.get("sla_seconds"),
                        tags=tc.get("tags", []),
                        domain=tc.get("domain"),
                        source="pipeline",
                    ))

        await self.db.commit()

    async def _persist_reviews(self, project_id: uuid.UUID, state: dict) -> None:
        """Save current agent reviews to the database."""
        reviews = state.get("current_reviews", [])
        phase_id = state.get("current_phase", 0)
        revision_round = state.get("revision_round", 1)

        for review in reviews:
            review_dict = asdict(review) if hasattr(review, "__dataclass_fields__") else review
            self.db.add(AgentReviewModel(
                project_id=project_id,
                phase_id=phase_id,
                agent_id=review_dict.get("agent_id", ""),
                agent_name=review_dict.get("agent_name", ""),
                role=review_dict.get("role", "reviewer"),
                status=review_dict.get("status", "approved"),
                confidence=review_dict.get("confidence"),
                comments=review_dict.get("comments", []),
                additions=review_dict.get("additions", []),
                revision_round=revision_round,
            ))

        # Also save the primary agent's consolidation
        primary_output = state.get("current_primary_output", {})
        consolidation_summary = state.get("current_consolidation_summary")
        if primary_output:
            self.db.add(AgentReviewModel(
                project_id=project_id,
                phase_id=phase_id,
                agent_id=primary_output.get("agent_id", ""),
                agent_name=primary_output.get("agent_name", ""),
                role="primary",
                status="consolidated",
                consolidation_summary=consolidation_summary,
                revision_round=revision_round,
            ))

        await self.db.commit()
