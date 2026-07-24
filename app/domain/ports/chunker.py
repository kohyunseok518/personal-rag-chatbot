from abc import ABC, abstractmethod

from app.domain.models import (
    DocumentChunk,
    SourceDocument,
)


class ChunkerPort(ABC):
    @abstractmethod
    def split(
        self,
        document: SourceDocument,
    ) -> list[DocumentChunk]:
        raise NotImplementedError