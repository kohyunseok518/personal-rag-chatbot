from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="개인 문서에 관한 질문",
        examples=[
            "분산 투자는 왜 필요한가요?"
        ],
    )

    @field_validator("question")
    @classmethod
    def validate_question(
        cls,
        question: str,
    ) -> str:
        normalized_question = question.strip()

        if not normalized_question:
            raise ValueError(
                "질문을 입력해 주세요."
            )

        return normalized_question