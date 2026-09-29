import logging

from fastapi import APIRouter, HTTPException

from app.db.database import check_database_connection

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "scientific-discovery-backend"}


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return health()


@router.get("/health/db")
def database_health() -> dict[str, str]:
    try:
        check_database_connection()
    except Exception as exc:
        logger.exception("database_health_check_failed")
        raise HTTPException(status_code=503, detail={"code": "database_unavailable", "message": str(exc)}) from exc
    return {"status": "ok", "database": "connected"}