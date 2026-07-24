from pydantic import BaseModel, Field


class SourceResponse(BaseModel):
    chunk_id: str = Field(
        description="검색된 청크의 고유 ID",
    )

    document_title: str = Field(
        description="원본 문서 제목",
    )

    rank: int = Field(
        ge=1,
        description="검색 순위",
    )

    score: float = Field(
        description="코사인 유사도 점수",
    )

    content: str = Field(
        description="답변 근거로 사용한 청크 내용",
    )