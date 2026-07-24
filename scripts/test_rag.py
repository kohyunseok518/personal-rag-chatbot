import argparse

from app.application.services import (
    ChatService,
    RetrievalService,
)
from app.core.config import get_settings
from app.infrastructure.embedding import (
    OpenAIEmbeddingProvider,
)
from app.infrastructure.llm import (
    OpenAIAnswerGenerator,
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
            "검색된 문서를 기반으로 "
            "LLM 답변을 생성합니다."
        ),
    )

    parser.add_argument(
        "question",
        nargs="?",
        default=DEFAULT_QUESTION,
        help="질문 내용",
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

    answer_generator = OpenAIAnswerGenerator(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    chat_service = ChatService(
        retrieval_service=retrieval_service,
        answer_generator=answer_generator,
    )

    print("=" * 70)
    print("RAG 답변 생성 테스트")
    print("=" * 70)
    print(f"질문: {arguments.question}")
    print(
        f"채팅 모델: "
        f"{answer_generator.model_name}"
    )
    print(
        f"임베딩 모델: "
        f"{settings.openai_embedding_model}"
    )

    result = chat_service.ask(
        question=arguments.question,
    )

    print()
    print("=" * 70)
    print("생성된 답변")
    print("=" * 70)
    print(result.answer)

    print()
    print(f"근거 기반 여부: {result.grounded}")

    print()
    print("=" * 70)
    print("사용된 출처")
    print("=" * 70)

    if not result.sources:
        print("사용된 출처가 없습니다.")
        return

    for source in result.sources:
        print(
            f"- {source.chunk.chunk_id}"
            f" | 점수: {source.score:.4f}"
            f" | 문서: "
            f"{source.chunk.document_title}"
        )


if __name__ == "__main__":
    main()