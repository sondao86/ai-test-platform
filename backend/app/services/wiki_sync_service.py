"""Azure DevOps Wiki sync service — clones wiki git repo and reads markdown."""

from __future__ import annotations

import asyncio
import logging
import shutil
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_CONTENT_SIZE = 10 * 1024 * 1024  # 10 MB
CLONE_TIMEOUT_SECONDS = 120


class WikiSyncService:
    """Sync markdown content from an Azure DevOps Wiki (git-based)."""

    def __init__(
        self,
        organization: str,
        project: str,
        wiki_name: str | None,
        pat: str,
    ):
        self.organization = organization
        self.project = project
        self.wiki_name = wiki_name or f"{project}.wiki"
        self._pat = pat

    async def sync_page(self, page_path: str | None = None) -> str:
        """Clone wiki repo and return markdown content.

        Args:
            page_path: Optional path to a specific wiki page.
                       If None, reads all .md files and concatenates them.

        Returns:
            Raw markdown content as a string.

        Raises:
            RuntimeError: On clone failure, page not found, or empty wiki.
        """
        tmp_dir = tempfile.mkdtemp(prefix="wiki_sync_")
        try:
            await self._clone_repo(tmp_dir)

            repo_root = Path(tmp_dir)

            if page_path:
                content = self._read_specific_page(repo_root, page_path)
            else:
                content = self._read_all_pages(repo_root)

            if len(content) > MAX_CONTENT_SIZE:
                logger.warning(
                    "Wiki content exceeds %d bytes, truncating", MAX_CONTENT_SIZE
                )
                content = content[:MAX_CONTENT_SIZE]

            return content
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    async def _clone_repo(self, dest_dir: str) -> None:
        """Git clone the wiki repo with depth 1."""
        clone_url = (
            f"https://{self._pat}@dev.azure.com/"
            f"{self.organization}/{self.project}/_git/{self.wiki_name}"
        )
        try:
            process = await asyncio.create_subprocess_exec(
                "git", "clone", "--depth", "1", clone_url, dest_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(
                process.communicate(), timeout=CLONE_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            raise RuntimeError(
                f"Git clone timed out after {CLONE_TIMEOUT_SECONDS}s"
            )

        if process.returncode != 0:
            error_msg = self._scrub_pat(stderr.decode(errors="replace"))
            raise RuntimeError(f"Git clone failed: {error_msg}")

    def _read_specific_page(self, repo_root: Path, page_path: str) -> str:
        """Find and read a specific wiki page.

        Azure DevOps Wiki uses hyphens for spaces in filenames,
        e.g. "My Page" → "My-Page.md".
        """
        # Try exact path first
        candidates = [
            repo_root / page_path,
            repo_root / f"{page_path}.md",
        ]

        # Also try hyphenated version (Azure Wiki convention)
        hyphenated = page_path.replace(" ", "-")
        candidates.extend([
            repo_root / hyphenated,
            repo_root / f"{hyphenated}.md",
        ])

        for candidate in candidates:
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")

        raise RuntimeError(
            f"Wiki page not found: {page_path} "
            f"(tried: {', '.join(c.name for c in candidates)})"
        )

    def _read_all_pages(self, repo_root: Path) -> str:
        """Read all .md files in the repo, concatenated with separators."""
        md_files = sorted(repo_root.rglob("*.md"))
        # Exclude common non-content files
        md_files = [
            f for f in md_files
            if ".git" not in f.parts
        ]

        if not md_files:
            raise RuntimeError("No .md files found in wiki repository")

        pages = []
        for md_file in md_files:
            relative = md_file.relative_to(repo_root)
            content = md_file.read_text(encoding="utf-8")
            pages.append(f"--- {relative} ---\n{content}")

        return "\n\n".join(pages)

    def _scrub_pat(self, text: str) -> str:
        """Remove PAT from error messages."""
        if self._pat:
            return text.replace(self._pat, "***")
        return text
