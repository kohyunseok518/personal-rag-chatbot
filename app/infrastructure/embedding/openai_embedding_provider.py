from collections.abc import Sequence

from langchain_openai import OpenAIEmbeddings

from app.core.exceptions import EmbeddingError
from app.domain.ports import EmbeddingProviderPort


class OpenAIEmbeddingProvider(
    EmbeddingProviderPort
):
    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        if not api_key.strip():
            raise EmbeddingError(
                message=(
                    "OPENAI_API_KEY가 설정되지 "
                    "않았습니다."
                ),
            )

        if not model.strip():
            raise EmbeddingError(
                message=(
                    "임베딩 모델 이름이 설정되지 "
                    "않았습니다."
                ),
            )

        self._model = model

        self._embeddings = OpenAIEmbeddings(
            model=model,
            api_key=api_key,
        )

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        normalized_texts = [
            text.strip()
            for text in texts
            if text.strip()
        ]

        if not normalized_texts:
            return []

        try:
            return self._embeddings.embed_documents(
                normalized_texts
            )
        except Exception as error:
            raise EmbeddingError(
                message=(
                    "문서 임베딩 생성에 "
                    "실패했습니다."
                ),
            ) from error

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        normalized_query = query.strip()

        if not normalized_query:
            raise EmbeddingError(
                message=(
                    "임베딩할 질문이 비어 있습니다."
                ),
            )

        try:
            return self._embeddings.embed_query(
                normalized_query
            )
        except Exception as error:
            raise EmbeddingError(
                message=(
                    "질문 임베딩 생성에 "
                    "실패했습니다."
                ),
            ) from error

    @property
    def model(self) -> str:
        return self._model