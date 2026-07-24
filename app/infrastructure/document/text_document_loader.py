import hashlib
import re
from pathlib import Path

from app.core.exceptions import DocumentLoadError
from app.domain.models import SourceDocument
from app.domain.ports import DocumentLoaderPort


class TextDocumentLoader(DocumentLoaderPort):
    SUPPORTED_SUFFIXES = {
        ".txt",
        ".md",
    }

    def load(
        self,
        file_path: Path,
    ) -> list[SourceDocument]:
        self._validate_file(file_path)

        content = self._read_file(file_path)
        document_id = self._create_document_id(
            file_path=file_path,
            content=content,
        )

        document = SourceDocument(
            document_id=document_id,
            title=file_path.stem,
            content=content,
            source=str(file_path),
            metadata={
                "source": str(file_path),
                "file_name": file_path.name,
                "file_extension": file_path.suffix.lower(),
                "character_count": len(content),
            },
        )

        return [document]

    def _validate_file(
        self,
        file_path: Path,
    ) -> None:
        if not file_path.exists():
            raise DocumentLoadError(
                message=(
                    f"문서 파일을 찾을 수 없습니다: "
                    f"{file_path}"
                ),
            )

        if not file_path.is_file():
            raise DocumentLoadError(
                message=(
                    f"파일이 아닌 경로입니다: "
                    f"{file_path}"
                ),
            )

        if (
            file_path.suffix.lower()
            not in self.SUPPORTED_SUFFIXES
        ):
            raise DocumentLoadError(
                message=(
                    "지원하지 않는 문서 형식입니다: "
                    f"{file_path.suffix}"
                ),
            )

    def _read_file(
        self,
        file_path: Path,
    ) -> str:
        try:
            content = file_path.read_text(
                encoding="utf-8-sig",
            )
        except (OSError, UnicodeDecodeError) as error:
            raise DocumentLoadError(
                message=(
                    "문서를 UTF-8 형식으로 읽지 "
                    f"못했습니다: {file_path.name}"
                ),
            ) from error

        normalized_content = self._normalize_text(
            content
        )

        if not normalized_content:
            raise DocumentLoadError(
                message=(
                    "문서에 내용이 없습니다: "
                    f"{file_path.name}"
                ),
            )

        return normalized_content

    def _normalize_text(
        self,
        content: str,
    ) -> str:
        content = content.replace(
            "\r\n",
            "\n",
        )
        content = content.replace(
            "\r",
            "\n",
        )
        content = content.replace(
            "\u00a0",
            " ",
        )

        lines = [
            line.rstrip()
            for line in content.splitlines()
        ]

        normalized_content = "\n".join(lines)

        normalized_content = re.sub(
            r"\n{3,}",
            "\n\n",
            normalized_content,
        )

        return normalized_content.strip()

    def _create_document_id(
        self,
        file_path: Path,
        content: str,
    ) -> str:
        normalized_stem = re.sub(
            r"[^0-9A-Za-z가-힣_-]+",
            "-",
            file_path.stem,
        ).strip("-")

        if not normalized_stem:
            normalized_stem = "document"

        content_hash = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()[:12]

        return (
            f"{normalized_stem.lower()}-"
            f"{content_hash}"
        )