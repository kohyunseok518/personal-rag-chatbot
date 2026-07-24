from app.core.exceptions import (
    InvalidQuestionError,
    RetrievalError,
)
from app.domain.models import RetrievedChunk
from app.domain.ports import (
    EmbeddingProviderPort,
    VectorStorePort,
)


class RetrievalService:
    def __init__(
        self,
        embedding_provider: EmbeddingProviderPort,
        vector_store: VectorStorePort,
        default_top_k: int,
    ) -> None:
        if default_top_k <= 0:
            raise ValueError(
                "default_top_k는 0보다 "
                "커야 합니다."
            )

        self._embedding_provider = (
            embedding_provider
        )
        self._vector_store = vector_store
        self._default_top_k = default_top_k

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        normalized_question = question.strip()

        if not normalized_question:
            raise InvalidQuestionError(
                message="질문을 입력해 주세요.",
            )

        resolved_top_k = (
            top_k
            if top_k is not None
            else self._default_top_k
        )

        if resolved_top_k <= 0:
            raise InvalidQuestionError(
                message=(
                    "검색할 문서 개수는 "
                    "0보다 커야 합니다."
                ),
            )

        query_vector = (
            self._embedding_provider
            .embed_query(normalized_question)
        )

        results = self._vector_store.search(
            query_vector=query_vector,
            top_k=resolved_top_k,
        )

        if not results:
            raise RetrievalError(
                message=(
                    "질문과 관련된 문서를 "
                    "찾지 못했습니다."
                ),
            )

        return results