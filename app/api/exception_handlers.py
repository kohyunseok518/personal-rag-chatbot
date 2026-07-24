import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    InvalidQuestionError,
    VectorStoreNotReadyError,
)


logger = logging.getLogger(__name__)


def get_status_code(exception: AppError) -> int:
    if isinstance(exception, InvalidQuestionError):
        return 400

    if isinstance(exception, VectorStoreNotReadyError):
        return 503

    return 500


def register_exception_handlers(application: FastAPI) -> None:
    @application.exception_handler(AppError)
    async def handle_app_error(
        request: Request,
        exception: AppError,
    ) -> JSONResponse:
        status_code = get_status_code(exception)

        logger.error(
            "application_error path=%s code=%s message=%s",
            request.url.path,
            exception.code,
            exception.message,
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exception.code,
                    "message": exception.message,
                }
            },
        )