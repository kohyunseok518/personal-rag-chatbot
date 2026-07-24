from pydantic import BaseModel, Field

from app.application.dto.source_response import (
    SourceResponse,
)


class ChatResponse(BaseModel):
    answer: str = Field(
        description="문서를 기반으로 생성한 답변",
    )

    grounded: bool = Field(
        description=(
            "답변이 검색 문서에 근거했는지 여부"
        ),
    )

    sources: list[SourceResponse] = Field(
        default_factory=list,
        description="답변 생성에 사용된 출처",
    )