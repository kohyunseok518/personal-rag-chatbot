from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.models import SourceDocument


class DocumentLoaderPort(ABC):
    @abstractmethod
    def load(
        self,
        file_path: Path,
    ) -> list[SourceDocument]:
        raise NotImplementedError