# Lessons Learned

## 2026-03-06: Domain Separation Violation
- **Mistake**: Created frontend files (React components, pages, types, API client) inside `frontend/` directory
- **Rule**: `CLAUDE.md` Section 7 explicitly states: "Do NOT read, modify, or create any files inside the `frontend/` directory"
- **Correct Approach**:
  1. Implement backend only (models, services, API endpoints, migrations)
  2. Update `API_SPEC.md` with the API contract for the new feature
  3. Let Gemini handle all frontend implementation based on the API spec
- **Pattern to avoid**: When implementing a full-stack feature, STOP at the API layer. Output the contract to `API_SPEC.md` and nothing more.
