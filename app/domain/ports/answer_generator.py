from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.models import (
    GeneratedAnswer,
    RetrievedChunk,
)


class AnswerGeneratorPort(ABC):
    @abstractmethod
    def generate(
        self,
        question: str,
        contexts: Sequence[RetrievedChunk],
    ) -> GeneratedAnswer:
        raise NotImplementedError