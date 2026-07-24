class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: str = "APPLICATION_ERROR",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class InvalidQuestionError(AppError):
    def __init__(
        self,
        message: str = "질문을 확인해 주세요.",
    ) -> None:
        super().__init__(
            message=message,
            code="INVALID_QUESTION",
        )


class DocumentLoadError(AppError):
    def __init__(
        self,
        message: str = "문서를 불러오지 못했습니다.",
    ) -> None:
        super().__init__(
            message=message,
            code="DOCUMENT_LOAD_ERROR",
        )


class VectorStoreNotReadyError(AppError):
    def __init__(
        self,
        message: str = "검색 인덱스가 준비되지 않았습니다.",
    ) -> None:
        super().__init__(
            message=message,
            code="VECTOR_STORE_NOT_READY",
        )


class RetrievalError(AppError):
    def __init__(
        self,
        message: str = "관련 문서를 검색하지 못했습니다.",
    ) -> None:
        super().__init__(
            message=message,
            code="RETRIEVAL_ERROR",
        )


class AnswerGenerationError(AppError):
    def __init__(
        self,
        message: str = "답변 생성에 실패했습니다.",
    ) -> None:
        super().__init__(
            message=message,
            code="ANSWER_GENERATION_ERROR",
        )