from collections.abc import Sequence

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.core.exceptions import (
    AnswerGenerationError,
)
from app.domain.models import (
    GeneratedAnswer,
    RetrievedChunk,
)
from app.domain.ports import AnswerGeneratorPort
from app.infrastructure.llm.prompts import (
    SYSTEM_PROMPT,
)


class StructuredAnswer(BaseModel):
    answer: str = Field(
        description=(
            "제공된 문서를 근거로 작성한 "
            "최종 한국어 답변"
        ),
    )

    grounded: bool = Field(
        description=(
            "답변이 제공된 문서의 근거만으로 "
            "충분히 작성되었는지 여부"
        ),
    )

    source_chunk_ids: list[str] = Field(
        description=(
            "답변에 실제로 사용한 청크 ID 목록"
        ),
    )


class OpenAIAnswerGenerator(
    AnswerGeneratorPort
):
    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        if not api_key.strip():
            raise AnswerGenerationError(
                message=(
                    "OPENAI_API_KEY가 설정되지 "
                    "않았습니다."
                ),
            )

        if not model.strip():
            raise AnswerGenerationError(
                message=(
                    "채팅 모델 이름이 설정되지 "
                    "않았습니다."
                ),
            )

        self._model_name = model

        chat_model = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0,
            max_retries=2,
            timeout=30,
        )

        self._structured_model = (
            chat_model.with_structured_output(
                StructuredAnswer,
                method="json_schema",
            )
        )

    def generate(
        self,
        question: str,
        contexts: Sequence[RetrievedChunk],
    ) -> GeneratedAnswer:
        normalized_question = question.strip()

        if not normalized_question:
            raise AnswerGenerationError(
                message=(
                    "답변을 생성할 질문이 "
                    "비어 있습니다."
                ),
            )

        if not contexts:
            return GeneratedAnswer(
                answer=(
                    "제공된 문서에서 답을 "
                    "찾을 수 없습니다."
                ),
                sources=(),
                grounded=False,
            )

        context_text = self._format_contexts(
            contexts
        )

        user_prompt = f"""
[사용자 질문]

{normalized_question}


[검색된 문서]

{context_text}


검색된 문서만 근거로 질문에 답변하세요.
""".strip()

        try:
            response = (
                self._structured_model.invoke(
                    [
                        SystemMessage(
                            content=SYSTEM_PROMPT
                        ),
                        HumanMessage(
                            content=user_prompt
                        ),
                    ]
                )
            )

            structured_answer = (
                self._validate_response(response)
            )
        except Exception as error:
            raise AnswerGenerationError(
                message=(
                    "OpenAI 모델을 이용한 "
                    "답변 생성에 실패했습니다."
                ),
            ) from error

        context_by_id = {
            context.chunk.chunk_id: context
            for context in contexts
        }

        valid_source_ids = {
            chunk_id
            for chunk_id
            in structured_answer.source_chunk_ids
            if chunk_id in context_by_id
        }

        valid_sources = tuple(
            context
            for context in contexts
            if (
                context.chunk.chunk_id
                in valid_source_ids
            )
        )

        grounded = bool(
            structured_answer.grounded
            and valid_sources
        )

        if not grounded:
            return GeneratedAnswer(
                answer=(
                    "제공된 문서에서 답을 "
                    "찾을 수 없습니다."
                ),
                sources=(),
                grounded=False,
            )

        return GeneratedAnswer(
            answer=structured_answer.answer.strip(),
            sources=valid_sources,
            grounded=True,
        )

    @property
    def model_name(self) -> str:
        return self._model_name

    def _format_contexts(
        self,
        contexts: Sequence[RetrievedChunk],
    ) -> str:
        formatted_contexts = []

        for context in contexts:
            chunk = context.chunk

            formatted_context = f"""
[청크 ID]
{chunk.chunk_id}

[문서 제목]
{chunk.document_title}

[검색 점수]
{context.score:.4f}

[내용]
{chunk.content}
""".strip()

            formatted_contexts.append(
                formatted_context
            )

        return "\n\n---\n\n".join(
            formatted_contexts
        )

    def _validate_response(
        self,
        response: object,
    ) -> StructuredAnswer:
        if isinstance(
            response,
            StructuredAnswer,
        ):
            return response

        return StructuredAnswer.model_validate(
            response
        )