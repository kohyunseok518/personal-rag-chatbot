from pathlib import Path

from app.application.services import (
    IndexingService,
)
from app.core.config import get_settings
from app.infrastructure.document import (
    RecursiveTextChunker,
    TextDocumentLoader,
)
from app.infrastructure.embedding import (
    OpenAIEmbeddingProvider,
)
from app.infrastructure.vector_store import (
    FaissVectorStore,
)


SUPPORTED_SUFFIXES = {
    ".txt",
    ".md",
}


def find_source_files(
    source_directory: Path,
) -> list[Path]:
    if not source_directory.exists():
        return []

    return sorted(
        file_path
        for file_path
        in source_directory.iterdir()
        if (
            file_path.is_file()
            and file_path.suffix.lower()
            in SUPPORTED_SUFFIXES
        )
    )


def main() -> None:
    settings = get_settings()

    source_files = find_source_files(
        settings.raw_document_path
    )

    index_storage_path = (
        settings.vector_store_path
        / settings.vector_index_name
    )

    document_loader = TextDocumentLoader()

    chunker = RecursiveTextChunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    embedding_provider = (
        OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=(
                settings.openai_embedding_model
            ),
        )
    )

    vector_store = FaissVectorStore(
        storage_path=index_storage_path,
    )

    indexing_service = IndexingService(
        document_loader=document_loader,
        chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    print("=" * 70)
    print("개인 문서 색인 시작")
    print("=" * 70)
    print(
        f"원본 문서 경로: "
        f"{settings.raw_document_path}"
    )
    print(
        f"검색된 파일 수: "
        f"{len(source_files):,}"
    )
    print(
        f"임베딩 모델: "
        f"{settings.openai_embedding_model}"
    )
    print(
        f"인덱스 저장 경로: "
        f"{index_storage_path}"
    )

    for file_path in source_files:
        print(f"- {file_path.name}")

    result = indexing_service.build_index(
        source_files
    )

    print()
    print("=" * 70)
    print("색인 완료")
    print("=" * 70)
    print(
        f"문서 수: "
        f"{result.document_count:,}"
    )
    print(
        f"청크 수: "
        f"{result.chunk_count:,}"
    )
    print(
        f"벡터 차원: "
        f"{result.vector_dimension:,}"
    )
    print(
        f"저장 위치: "
        f"{index_storage_path}"
    )


if __name__ == "__main__":
    main()