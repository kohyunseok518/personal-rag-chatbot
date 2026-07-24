from dataclasses import dataclass

from app.domain.models.retrieved_chunk import (
    RetrievedChunk,
)


@dataclass(
    frozen=True,
    slots=True,
)
class GeneratedAnswer:
    answer: str
    sources: tuple[RetrievedChunk, ...]
    grounded: bool

    def __post_init__(self) -> None:
        if not self.answer.strip():
            raise ValueError(
                "생성된 답변은 비어 있을 수 없습니다."
            )