from fastapi import APIRouter

from app.api.v1 import projects, phases, workflow, executions

api_router = APIRouter()
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(phases.router, prefix="/projects", tags=["phases"])
api_router.include_router(workflow.router, prefix="/projects", tags=["workflow"])
api_router.include_router(executions.router, prefix="/projects", tags=["executions"])
