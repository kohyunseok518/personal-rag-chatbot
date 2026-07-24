# 여러 API 서버를 하나의 서버로 조립
from fastapi import FastAPI

from app.api.routes.health import router as health_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="Personal Knowledge RAG Chatbot",
        description="개인 문서 기반 로컬 RAG 챗봇",
        version="0.1.0",
    )

    application.include_router(health_router)

    return application


app = create_app()