"""Claude CLI wrapper — calls `claude -p` as subprocess instead of Anthropic API."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ClaudeResponse:
    """Response from Claude CLI."""

    text: str
    cost_usd: float | None = None
    duration_ms: int | None = None
    session_id: str | None = None
    is_error: bool = False


async def call_claude(
    prompt: str,
    system_prompt: str | None = None,
    model: str | None = None,
    json_schema: dict | None = None,
    max_budget_usd: float | None = None,
    timeout: int = 300,
) -> ClaudeResponse:
    """Call Claude CLI in non-interactive mode.

    Uses `claude -p` with --output-format json for structured responses.
    Tools are disabled (--tools "") so it acts as a pure LLM.
    """
    cmd = [
        "claude",
        "-p",
        "--output-format", "json",
        "--model", model or settings.claude_model,
        "--tools", "",  # disable tools — pure LLM
        "--no-session-persistence",
    ]

    if system_prompt:
        cmd += ["--system-prompt", system_prompt]

    if json_schema:
        cmd += ["--json-schema", json.dumps(json_schema)]

    if max_budget_usd:
        cmd += ["--max-budget-usd", str(max_budget_usd)]

    cmd.append(prompt)

    # Remove CLAUDECODE env var to allow nested invocation
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    logger.debug("Calling claude CLI: model=%s, prompt_len=%d", model or settings.claude_model, len(prompt))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise TimeoutError(f"Claude CLI timed out after {timeout}s")

    stdout_str = stdout.decode()
    stderr_str = stderr.decode()

    if proc.returncode != 0:
        logger.error("Claude CLI error (code %d): %s", proc.returncode, stderr_str)
        raise RuntimeError(f"Claude CLI exited with code {proc.returncode}: {stderr_str}")

    # Parse JSON response
    try:
        data = json.loads(stdout_str)
    except json.JSONDecodeError:
        # Fallback: treat entire stdout as plain text
        return ClaudeResponse(text=stdout_str.strip())

    return ClaudeResponse(
        text=data.get("result", stdout_str),
        cost_usd=data.get("total_cost_usd"),
        duration_ms=data.get("duration_ms"),
        session_id=data.get("session_id"),
        is_error=data.get("is_error", False),
    )


def parse_json_from_text(text: str) -> dict | list | None:
    """Extract JSON from Claude's text response.

    Handles responses that may contain markdown code blocks wrapping JSON.
    """
    # Try direct parse first
    stripped = text.strip()
    if stripped.startswith(("{", "[")):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

    # Find JSON in response (might be inside ```json ... ```)
    json_start = text.find("[")
    json_start_obj = text.find("{")
    if json_start == -1 or (json_start_obj != -1 and json_start_obj < json_start):
        json_start = json_start_obj

    json_end = max(text.rfind("]"), text.rfind("}"))
    if json_start != -1 and json_end != -1:
        try:
            return json.loads(text[json_start : json_end + 1])
        except json.JSONDecodeError:
            pass

    return None
