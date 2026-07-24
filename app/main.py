# 여러 API 서버를 하나의 서버로 조립
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router
from app.core.config import get_settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    settings = get_settings()

    settings.raw_document_path.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.vector_store_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "application_started environment=%s",
        settings.app_env,
    )

    yield

    logger.info("application_stopped")


def create_app() -> FastAPI:
    settings = get_settings()

    configure_logging(settings.log_level)

    application = FastAPI(
        title=settings.app_name,
        description="개인 문서 기반 로컬 RAG 챗봇",
        version="0.1.0",
        lifespan=lifespan,
    )

    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(chat_router)

    return application


app = create_app()