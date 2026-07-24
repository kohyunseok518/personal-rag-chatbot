from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_chat_service,
)
from app.application.dto import (
    ChatRequest,
    ChatResponse,
    SourceResponse,
)
from app.application.services import ChatService


router = APIRouter(
    prefix="/api",
    tags=["chat"],
)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    chat_service: Annotated[
        ChatService,
        Depends(get_chat_service),
    ],
) -> ChatResponse:
    result = chat_service.ask(
        question=request.question,
    )

    sources = [
        SourceResponse(
            chunk_id=source.chunk.chunk_id,
            document_title=(
                source.chunk.document_title
            ),
            rank=source.rank,
            score=source.score,
            content=source.chunk.content,
        )
        for source in result.sources
    ]

    return ChatResponse(
        answer=result.answer,
        grounded=result.grounded,
        sources=sources,
    )