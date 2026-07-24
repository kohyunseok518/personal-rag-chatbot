from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from app.domain.models import (
    DocumentChunk,
    SourceDocument,
)
from app.domain.ports import ChunkerPort


class RecursiveTextChunker(ChunkerPort):
    SEPARATORS = [
        "\n\n", # 문단
        "\n", # 줄
        ". ", 
        "? ",
        "! ",
        "。", # 전각 마침표
        " ",
        "", # 문자 단위
    ]

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        self._validate_settings(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self._splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=self.SEPARATORS,
                length_function=len,
                is_separator_regex=False,
            )
        )

    def split(
        self,
        document: SourceDocument,
    ) -> list[DocumentChunk]:
        split_texts = self._splitter.split_text(
            document.content
        )

        chunks = []

        for chunk_index, content in enumerate(
            split_texts
        ):
            normalized_content = content.strip()

            if not normalized_content:
                continue

            chunk_id = (
                f"{document.document_id}-"
                f"{chunk_index:04d}"
            )

            chunk_metadata = dict(
                document.metadata
            )
            chunk_metadata.update(
                {
                    "chunk_index": chunk_index,
                    "chunk_character_count": len(
                        normalized_content
                    ),
                }
            )

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document.document_id,
                document_title=document.title,
                content=normalized_content,
                chunk_index=chunk_index,
                metadata=chunk_metadata,
            )

            chunks.append(chunk)

        return chunks

    def _validate_settings(
        self,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size는 0보다 커야 합니다."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap은 0 이상이어야 합니다."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap은 chunk_size보다 "
                "작아야 합니다."
            )