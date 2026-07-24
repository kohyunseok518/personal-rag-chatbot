from functools import lru_cache

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


@lru_cache
def get_embedding_provider(
) -> OpenAIEmbeddingProvider:
    settings = get_settings()

    return OpenAIEmbeddingProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )


@lru_cache
def get_vector_store() -> FaissVectorStore:
    settings = get_settings()

    index_storage_path = (
        settings.vector_store_path
        / settings.vector_index_name
    )

    vector_store = FaissVectorStore(
        storage_path=index_storage_path,
    )

    vector_store.load()

    return vector_store


@lru_cache
def get_retrieval_service(
) -> RetrievalService:
    settings = get_settings()

    return RetrievalService(
        embedding_provider=(
            get_embedding_provider()
        ),
        vector_store=get_vector_store(),
        default_top_k=settings.search_top_k,
    )


@lru_cache
def get_answer_generator(
) -> OpenAIAnswerGenerator:
    settings = get_settings()

    return OpenAIAnswerGenerator(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(
        retrieval_service=(
            get_retrieval_service()
        ),
        answer_generator=(
            get_answer_generator()
        ),
    )