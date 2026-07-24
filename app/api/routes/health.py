# 기능별 API 정의
from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(
    prefix="/api",
    tags=["health"],
)


@router.get("/health")
def health_check() -> dict[str, str]:
    settings = get_settings()

    return {
        "status": "ok",
        "enviroment": settings.app_env,
    }