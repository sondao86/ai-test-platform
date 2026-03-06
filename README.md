# ai-test-platform

AI-powered multi-agent test automation platform. Uses Claude and Gemini agents to analyze business requirements, generate test cases, and execute them automatically.

## Project Structure

See [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) for the full folder layout and conventions.

Use this as a reference when creating new AI agentic projects:

```
/
├── CLAUDE.md / GEMINI.md        # Agent rules (project root)
├── docs/                        # Unified documentation
│   ├── api/                     #   API contract
│   ├── backend/                 #   Backend architecture & data model
│   ├── frontend/                #   UI/UX specs
│   ├── framework/               #   Multi-agent framework design
│   └── testing/                 #   QA strategy
├── tasks/                       # AI task tracking & lessons learned
├── backend/                     # Python / FastAPI
└── frontend/                    # Next.js
```

## Getting Started

```bash
# Backend
cd backend
cp .env.example .env
docker compose up -d

# Frontend
cd frontend
npm install
npm run dev
```