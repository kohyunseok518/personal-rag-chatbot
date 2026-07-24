from dataclasses import dataclass

from app.domain.models.document import DocumentChunk


@dataclass(
    frozen=True,
    slots=True,
)
class RetrievedChunk:
    chunk: DocumentChunk
    score: float
    rank: int

    def __post_init__(self) -> None:
        if self.rank < 1:
            raise ValueError(
                "검색 순위는 1 이상이어야 합니다."
            )