from app.application.services.retrieval_service import (
    RetrievalService,
)
from app.domain.models import GeneratedAnswer
from app.domain.ports import AnswerGeneratorPort


class ChatService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        answer_generator: AnswerGeneratorPort,
    ) -> None:
        self._retrieval_service = (
            retrieval_service
        )
        self._answer_generator = (
            answer_generator
        )

    def ask(
        self,
        question: str,
    ) -> GeneratedAnswer:
        contexts = (
            self._retrieval_service.retrieve(
                question=question,
            )
        )

        return self._answer_generator.generate(
            question=question,
            contexts=contexts,
        )