import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.routes.read_only import router as catalog_router
from app.api.routes.science import router as science_router
from app.core.config import get_settings
from app.core.exceptions import ScientificError
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("scientific_backend_started")
    yield
    logger.info("scientific_backend_stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.software_version,
    description=(
        "A reproducible foundation for candidate mathematical relationships. "
        "It records experiments and evidence; it does not establish scientific truth."
    ),
    lifespan=lifespan,
)


@app.exception_handler(ScientificError)
async def scientific_error_handler(_: Request, exc: ScientificError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


app.include_router(health_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")
app.include_router(science_router, prefix="/api")