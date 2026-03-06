"""Export service — generates hybrid folder structure + ZIP for test cases."""

from __future__ import annotations

import io
import logging
import re
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.requirement import Requirement
from app.models.test_case import TestCase
from app.models.test_category_map import TestCategoryMap

logger = logging.getLogger(__name__)

_UNASSIGNED_DOMAIN = "_unassigned"


class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_test_cases(
        self,
        project_id: uuid.UUID,
        output_dir: str | None = None,
    ) -> dict:
        """Export active test cases as a hybrid domain-first folder structure ZIP.

        Returns dict with project_id, total_tests, domains, export_path, message.
        """
        # 1. Load project
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # 2. Load active test cases
        tc_result = await self.db.execute(
            select(TestCase).where(
                TestCase.project_id == project_id,
                TestCase.is_active == True,  # noqa: E712
            )
        )
        test_cases = list(tc_result.scalars().all())

        # 3. Load requirements for traceability
        req_result = await self.db.execute(
            select(Requirement).where(Requirement.project_id == project_id)
        )
        requirements = list(req_result.scalars().all())
        req_map = {str(r.id): r for r in requirements}

        # 4. Load category mappings to resolve requirement links
        tcm_result = await self.db.execute(
            select(TestCategoryMap).where(TestCategoryMap.project_id == project_id)
        )
        category_maps = list(tcm_result.scalars().all())
        tcm_map = {str(cm.id): cm for cm in category_maps}

        # 5. Build sanitised project name for folder
        safe_name = re.sub(r"[^\w\-]", "_", project.name.lower())
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        root_dir = f"export_{safe_name}_{timestamp}"

        # 6. Group test cases by domain
        domain_groups: dict[str, list[TestCase]] = {}
        for tc in test_cases:
            domain = tc.domain or _UNASSIGNED_DOMAIN
            domain_groups.setdefault(domain, []).append(tc)

        # 7. Build ZIP in-memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Handle empty export
            if not test_cases:
                zf.writestr(
                    f"{root_dir}/README.md",
                    "# Export\n\nNo active test cases found for this project.\n",
                )
            else:
                # _shared/ placeholder
                zf.writestr(
                    f"{root_dir}/_shared/README.md",
                    "# Shared Resources\n\nPlace shared macros, fixtures, or utilities here.\n",
                )

                for domain, tcs in sorted(domain_groups.items()):
                    # Write individual test YAML files
                    for tc in tcs:
                        req = self._resolve_requirement(tc, tcm_map, req_map)
                        yaml_content = self._build_test_yaml(tc, req)
                        layer = tc.pipeline_layer or "bronze"
                        category = tc.test_category or "data_quality"
                        file_path = f"{root_dir}/{domain}/{layer}/{category}/{tc.test_id}.yml"
                        zf.writestr(file_path, yaml_content)

                    # Write _test_meta.yml per domain
                    meta_content = self._build_test_meta(domain, tcs, tcm_map, req_map)
                    zf.writestr(f"{root_dir}/{domain}/_test_meta.yml", meta_content)

        # 8. Write ZIP to disk
        if output_dir:
            dest = Path(output_dir)
        else:
            dest = Path(tempfile.mkdtemp(prefix="brd_export_"))
        dest.mkdir(parents=True, exist_ok=True)
        zip_path = dest / f"{root_dir}.zip"
        zip_path.write_bytes(zip_buffer.getvalue())

        domains = sorted(domain_groups.keys())
        logger.info(
            "Exported %d test cases for project %s → %s",
            len(test_cases), project_id, zip_path,
        )

        return {
            "project_id": str(project_id),
            "total_tests": len(test_cases),
            "domains": domains,
            "export_path": str(zip_path),
            "message": f"Exported {len(test_cases)} test cases across {len(domains)} domain(s).",
        }

    # --- Internal helpers ---

    def _resolve_requirement(
        self,
        tc: TestCase,
        tcm_map: dict[str, TestCategoryMap],
        req_map: dict[str, Requirement],
    ) -> Requirement | None:
        """Walk TestCase → TestCategoryMap → Requirement."""
        if not tc.category_map_id:
            return None
        tcm = tcm_map.get(str(tc.category_map_id))
        if not tcm or not tcm.requirement_id:
            return None
        return req_map.get(str(tcm.requirement_id))

    def _build_structured_tags(self, tc: TestCase, req: Requirement | None) -> list[str]:
        """Build structured tag list from test case attributes."""
        tags: list[str] = []
        if tc.domain:
            tags.append(f"domain:{tc.domain}")
        if tc.pipeline_layer:
            tags.append(f"layer:{tc.pipeline_layer}")
        if tc.test_category:
            tags.append(f"category:{tc.test_category}")
        if tc.priority:
            tags.append(f"priority:P{tc.priority}")
        if req:
            tags.append(f"req:{req.requirement_id}")
        return tags

    def _build_test_yaml(self, tc: TestCase, req: Requirement | None) -> str:
        """Generate YAML content for a single test case file."""
        tags = self._build_structured_tags(tc, req)
        domain = tc.domain or _UNASSIGNED_DOMAIN
        layer = tc.pipeline_layer or "bronze"
        category = tc.test_category or "data_quality"

        req_comment = ""
        if req:
            req_comment = f"# Requirement: {req.requirement_id} — {req.title}\n"

        header = (
            f"# Auto-generated by BRD Test Pipeline\n"
            f"{req_comment}"
            f"# Domain: {domain} | Layer: {layer} | Category: {category}\n\n"
        )

        # If dbt_test_yaml exists, use it as the base and inject tags
        if tc.dbt_test_yaml:
            try:
                dbt_data = yaml.safe_load(tc.dbt_test_yaml)
                if isinstance(dbt_data, dict):
                    self._inject_tags_into_dbt(dbt_data, tags)
                    return header + yaml.dump(dbt_data, default_flow_style=False, sort_keys=False)
            except yaml.YAMLError:
                pass
            return header + tc.dbt_test_yaml

        # Build a dbt-compatible YAML structure
        model_name = f"{layer}_{domain}_{'_'.join(category.split('_')[:2])}"
        test_config: dict = {
            "config": {
                "severity": tc.severity or "medium",
                "tags": tags,
            },
            "meta": {
                "description": tc.description,
            },
        }
        if tc.sql_logic:
            test_config["meta"]["sql_logic"] = tc.sql_logic

        if tc.great_expectations_config:
            test_config["meta"]["great_expectations_config"] = tc.great_expectations_config

        test_name = re.sub(r"[^\w]", "_", tc.title.lower())[:60]
        doc: dict = {
            "models": [
                {
                    "name": model_name,
                    "tests": [
                        {test_name: test_config},
                    ],
                }
            ]
        }

        return header + yaml.dump(doc, default_flow_style=False, sort_keys=False)

    def _inject_tags_into_dbt(self, dbt_data: dict, tags: list[str]) -> None:
        """Inject structured tags into existing dbt YAML config."""
        models = dbt_data.get("models", [])
        for model in models:
            if not isinstance(model, dict):
                continue
            for test_list in (model.get("tests", []), model.get("columns", [])):
                if not isinstance(test_list, list):
                    continue
                for item in test_list:
                    if isinstance(item, dict):
                        for key, val in item.items():
                            if isinstance(val, dict):
                                config = val.setdefault("config", {})
                                config["tags"] = tags

    def _build_test_meta(
        self,
        domain: str,
        test_cases: list[TestCase],
        tcm_map: dict[str, TestCategoryMap],
        req_map: dict[str, Requirement],
    ) -> str:
        """Generate _test_meta.yml traceability file for a domain."""
        tests_meta: list[dict] = []
        for tc in sorted(test_cases, key=lambda t: t.test_id):
            req = self._resolve_requirement(tc, tcm_map, req_map)
            layer = tc.pipeline_layer or "bronze"
            category = tc.test_category or "data_quality"
            entry: dict = {
                "test_file": f"{layer}/{category}/{tc.test_id}.yml",
                "test_id": tc.test_id,
                "req_id": req.requirement_id if req else None,
                "category": category,
                "priority": tc.priority,
                "severity": tc.severity,
                "description": tc.title,
            }
            tests_meta.append(entry)

        meta_doc = {"domain": domain, "tests": tests_meta}
        return yaml.dump(meta_doc, default_flow_style=False, sort_keys=False)
