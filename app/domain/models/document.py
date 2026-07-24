from dataclasses import dataclass, field
from typing import Any

# SourceDocument 객체는 청킹되지 않은 원본 문서
@dataclass(
    frozen=True,
    slots=True,
)
class SourceDocument:
    document_id: str
    title: str
    content: str
    source: str
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        if not self.document_id.strip():
            raise ValueError(
                "document_id는 비어 있을 수 없습니다."
            )

        if not self.title.strip():
            raise ValueError(
                "title은 비어 있을 수 없습니다."
            )

        if not self.content.strip():
            raise ValueError(
                "content는 비어 있을 수 없습니다."
            )
        
# DocumnetChunk 객체는 원본 문서를 청킹한 청크 객체
@dataclass(
    # frozen은 불변으로 만들고 slots은 정의되지 않은 속성을 객체에 추가하지 못하게 함
    frozen=True,
    slots=True,
)
class DocumentChunk:
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    chunk_index: int
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        if not self.chunk_id.strip():
            raise ValueError(
                "chunk_id는 비어 있을 수 없습니다."
            )

        if not self.document_id.strip():
            raise ValueError(
                "document_id는 비어 있을 수 없습니다."
            )

        if not self.content.strip():
            raise ValueError(
                "청크 내용은 비어 있을 수 없습니다."
            )

        if self.chunk_index < 0:
            raise ValueError(
                "chunk_index는 0 이상이어야 합니다."
            )