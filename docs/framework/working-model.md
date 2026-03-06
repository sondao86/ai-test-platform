# The AI Collaboration Framework (Multi-Agent Setup)

This document defines the workflow for coordinating between **Claude** (Full-Stack Developer) and **Gemini** (UI/UX Reviewer) to build features.

## The Development Workflow

### Step 1: Feature Ideation & Backlog (Product Owner)
When you have a new feature idea, open `docs/backlog.md` and add it to the **To Do** column. When you decide to start working on it, move it to **Doing**.

### Step 2: Create Requirements (Single Source of Truth)
Create a new Markdown file: `improvements/improvement-X-[name].md` (copy from `improvements/_template.md`). Write the feature description in natural language.

> **Example:**
> - *Feature: Add comment/feedback functionality to document review.*
> - *Requirement: Managers can highlight text and leave inline comments.*

### Step 3: Assign to Claude (Full-Stack)
Open the terminal running the `claude` agent and hand it the requirements file.

**Example command:**
```
@[improvements/improvement-X-[name].md] Design and implement the solution for this feature.
Setup database schema, update docs/architecture.md, write the API backend and frontend,
and output the contract to API_SPEC.md. Write an enhancement doc for Gemini UI/UX review.
```

**Claude will:**
1. Code the full-stack implementation (backend + frontend).
2. Update the system design in `docs/architecture.md`.
3. Write the API contract to `API_SPEC.md`.
4. Write an enhancement doc for Gemini UI/UX review.

### Step 4: Gemini Reviews UI/UX
Switch to the IDE chat with Gemini and give a single command to review Claude's enhancement doc.

**Example command:**
```
@[improvements/improvement-X-[name].md] Claude implemented the feature and wrote
an enhancement doc. Review the UI/UX approach and approve or request changes.
```

**Gemini will:**
1. Read the enhancement doc and review the UI/UX approach, user flow, and visual consistency.
2. Approve the implementation or request specific changes.
3. Gemini does NOT write code — only provides review feedback.

### Step 5: Completion & Logging
When both UI and API are working:
1. Test on localhost — verify end-to-end.
2. Open `docs/backlog.md` and move the feature to **Done**.
3. Save any lessons learned (if bugs occurred) to `tasks/lessons.md` so the AI avoids repeating mistakes.
