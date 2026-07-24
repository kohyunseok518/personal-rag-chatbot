from collections.abc import Sequence
from pathlib import Path

from app.application.dto import IndexingResult
from app.core.exceptions import (
    DocumentLoadError,
    VectorStoreError,
)
from app.domain.models import (
    DocumentChunk,
    SourceDocument,
)
from app.domain.ports import (
    ChunkerPort,
    DocumentLoaderPort,
    EmbeddingProviderPort,
    VectorStorePort,
)


class IndexingService:
    def __init__(
        self,
        document_loader: DocumentLoaderPort,
        chunker: ChunkerPort,
        embedding_provider: EmbeddingProviderPort,
        vector_store: VectorStorePort,
    ) -> None:
        self._document_loader = document_loader
        self._chunker = chunker
        self._embedding_provider = (
            embedding_provider
        )
        self._vector_store = vector_store

    def build_index(
        self,
        file_paths: Sequence[Path],
    ) -> IndexingResult:
        if not file_paths:
            raise DocumentLoadError(
                message=(
                    "색인할 문서 파일이 없습니다."
                ),
            )

        documents: list[SourceDocument] = []
        chunks: list[DocumentChunk] = []

        for file_path in file_paths:
            loaded_documents = (
                self._document_loader.load(
                    file_path
                )
            )

            documents.extend(
                loaded_documents
            )

            for document in loaded_documents:
                document_chunks = (
                    self._chunker.split(
                        document
                    )
                )
                chunks.extend(document_chunks)

        if not chunks:
            raise DocumentLoadError(
                message=(
                    "문서에서 생성된 청크가 "
                    "없습니다."
                ),
            )

        texts = [
            chunk.content
            for chunk in chunks
        ]

        vectors = (
            self._embedding_provider
            .embed_documents(texts)
        )

        if len(chunks) != len(vectors):
            raise VectorStoreError(
                message=(
                    "생성된 청크 수와 임베딩 "
                    "벡터 수가 일치하지 않습니다."
                ),
            )

        self._vector_store.create(
            chunks=chunks,
            vectors=vectors,
        )
        self._vector_store.save()

        vector_dimension = (
            len(vectors[0])
            if vectors
            else 0
        )

        return IndexingResult(
            document_count=len(documents),
            chunk_count=len(chunks),
            vector_dimension=vector_dimension,
        )