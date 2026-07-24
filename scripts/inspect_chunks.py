import argparse
from pathlib import Path

from app.core.config import get_settings
from app.infrastructure.document import (
    RecursiveTextChunker,
    TextDocumentLoader,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "TXT 문서를 로드하고 청킹 결과를 "
            "확인합니다."
        ),
    )

    parser.add_argument(
        "file_path",
        type=Path,
        help="확인할 TXT 파일 경로",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    settings = get_settings()

    loader = TextDocumentLoader()

    chunker = RecursiveTextChunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    documents = loader.load(
        arguments.file_path
    )

    all_chunks = []

    for document in documents:
        document_chunks = chunker.split(
            document
        )
        all_chunks.extend(document_chunks)

        print("=" * 70)
        print(f"문서 ID: {document.document_id}")
        print(f"문서 제목: {document.title}")
        print(f"문서 출처: {document.source}")
        print(
            f"전체 글자 수: "
            f"{len(document.content):,}"
        )
        print(
            f"생성된 청크 수: "
            f"{len(document_chunks):,}"
        )

    print("=" * 70)
    print("청킹 결과")
    print("=" * 70)

    for chunk in all_chunks:
        print()
        print("-" * 70)
        print(f"청크 ID: {chunk.chunk_id}")
        print(
            f"청크 순서: {chunk.chunk_index}"
        )
        print(
            f"청크 글자 수: "
            f"{len(chunk.content):,}"
        )
        print()
        print(chunk.content)

    print()
    print("=" * 70)
    print(f"전체 청크 수: {len(all_chunks):,}")


if __name__ == "__main__":
    main()