from abc import ABC, abstractmethod
from collections.abc import Sequence


class EmbeddingProviderPort(ABC):
    @abstractmethod
    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        raise NotImplementedError

    @abstractmethod
    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        raise NotImplementedError