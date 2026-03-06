import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import settings
from app.core.database import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.basicConfig(level=settings.log_level)
    logger.info("Starting BRD Test Pipeline API")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    yield

    # Shutdown
    await engine.dispose()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="BRD Test Pipeline",
        description="Multi-Agent BRD to Data Pipeline Test Case Generator",
        version="0.1.0",
        lifespan=lifespan,
    )

    from app.api.v1.router import api_router

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
