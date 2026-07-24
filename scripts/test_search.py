import argparse

from app.application.services import (
    RetrievalService,
)
from app.core.config import get_settings
from app.infrastructure.embedding import (
    OpenAIEmbeddingProvider,
)
from app.infrastructure.vector_store import (
    FaissVectorStore,
)


DEFAULT_QUESTION = (
    "분산 투자는 왜 필요한가요?"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "저장된 FAISS 인덱스에서 "
            "관련 청크를 검색합니다."
        ),
    )

    parser.add_argument(
        "question",
        nargs="?",
        default=DEFAULT_QUESTION,
        help="검색할 질문",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    settings = get_settings()

    index_storage_path = (
        settings.vector_store_path
        / settings.vector_index_name
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

    vector_store.load()

    retrieval_service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        default_top_k=settings.search_top_k,
    )

    print("=" * 70)
    print("벡터 검색 테스트")
    print("=" * 70)
    print(f"질문: {arguments.question}")
    print(
        f"인덱스: "
        f"{settings.vector_index_name}"
    )
    print(
        f"저장된 청크 수: "
        f"{vector_store.count:,}"
    )
    print(
        f"벡터 차원: "
        f"{vector_store.dimension:,}"
    )

    results = retrieval_service.retrieve(
        question=arguments.question,
    )

    print()
    print("=" * 70)
    print("검색 결과")
    print("=" * 70)

    for result in results:
        chunk = result.chunk

        print()
        print("-" * 70)
        print(f"순위: {result.rank}")
        print(
            f"유사도 점수: "
            f"{result.score:.4f}"
        )
        print(f"청크 ID: {chunk.chunk_id}")
        print(
            f"문서 제목: "
            f"{chunk.document_title}"
        )
        print(
            f"청크 순서: "
            f"{chunk.chunk_index}"
        )
        print()
        print(chunk.content)


if __name__ == "__main__":
    main()