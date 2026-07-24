from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.models import (
    DocumentChunk,
    RetrievedChunk,
)


class VectorStorePort(ABC):
    @abstractmethod
    def create(
        self,
        chunks: Sequence[DocumentChunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def save(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_vector: Sequence[float],
        top_k: int,
    ) -> list[RetrievedChunk]:
        raise NotImplementedError