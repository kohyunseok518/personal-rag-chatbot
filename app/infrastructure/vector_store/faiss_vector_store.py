import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.core.exceptions import (
    VectorStoreError,
    VectorStoreNotReadyError,
)
from app.domain.models import (
    DocumentChunk,
    RetrievedChunk,
)
from app.domain.ports import VectorStorePort


class FaissVectorStore(VectorStorePort):
    INDEX_FILE_NAME = "index.faiss"
    CHUNKS_FILE_NAME = "chunks.json"
    MANIFEST_FILE_NAME = "manifest.json"

    def __init__(
        self,
        storage_path: Path,
    ) -> None:
        self._storage_path = storage_path
        self._index: Any | None = None
        self._chunks: list[DocumentChunk] = []

    def create(
        self,
        chunks: Sequence[DocumentChunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        if not chunks:
            raise VectorStoreError(
                message="저장할 청크가 없습니다.",
            )

        if len(chunks) != len(vectors):
            raise VectorStoreError(
                message=(
                    "청크 개수와 벡터 개수가 "
                    "일치하지 않습니다."
                ),
            )

        matrix = np.asarray(
            vectors,
            dtype=np.float32,
        )

        if (
            matrix.ndim != 2
            or matrix.shape[1] == 0
        ):
            raise VectorStoreError(
                message=(
                    "임베딩 벡터의 형태가 "
                    "올바르지 않습니다."
                ),
            )

        if not np.isfinite(matrix).all():
            raise VectorStoreError(
                message=(
                    "임베딩 벡터에 유효하지 않은 "
                    "숫자가 포함되어 있습니다."
                ),
            )

        matrix = np.ascontiguousarray(matrix)

        # 내적을 코사인 유사도로 사용하기 위해
        # 각 벡터의 길이를 1로 정규화한다.
        faiss.normalize_L2(matrix)

        dimension = matrix.shape[1]

        index = faiss.IndexFlatIP(dimension)
        index.add(matrix)

        self._index = index
        self._chunks = list(chunks)

    def save(self) -> None:
        if self._index is None:
            raise VectorStoreNotReadyError(
                message=(
                    "저장할 FAISS 인덱스가 "
                    "생성되지 않았습니다."
                ),
            )

        if not self._chunks:
            raise VectorStoreNotReadyError(
                message=(
                    "저장할 청크 정보가 없습니다."
                ),
            )

        self._storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        index_path = (
            self._storage_path
            / self.INDEX_FILE_NAME
        )
        chunks_path = (
            self._storage_path
            / self.CHUNKS_FILE_NAME
        )
        manifest_path = (
            self._storage_path
            / self.MANIFEST_FILE_NAME
        )

        chunk_payload = [
            self._serialize_chunk(chunk)
            for chunk in self._chunks
        ]

        manifest_payload = {
            "chunk_count": len(self._chunks),
            "vector_count": int(
                self._index.ntotal
            ),
            "vector_dimension": int(
                self._index.d
            ),
            "similarity_metric": (
                "cosine_similarity"
            ),
        }

        try:
            faiss.write_index(
                self._index,
                str(index_path),
            )

            chunks_path.write_text(
                json.dumps(
                    chunk_payload,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                ),
                encoding="utf-8",
            )

            manifest_path.write_text(
                json.dumps(
                    manifest_payload,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except (OSError, RuntimeError) as error:
            raise VectorStoreError(
                message=(
                    "FAISS 인덱스를 파일로 "
                    "저장하지 못했습니다."
                ),
            ) from error

    def load(self) -> None:
        index_path = (
            self._storage_path
            / self.INDEX_FILE_NAME
        )
        chunks_path = (
            self._storage_path
            / self.CHUNKS_FILE_NAME
        )

        if not index_path.exists():
            raise VectorStoreNotReadyError(
                message=(
                    "저장된 FAISS 인덱스를 "
                    f"찾을 수 없습니다: {index_path}"
                ),
            )

        if not chunks_path.exists():
            raise VectorStoreNotReadyError(
                message=(
                    "저장된 청크 정보를 "
                    f"찾을 수 없습니다: {chunks_path}"
                ),
            )

        try:
            index = faiss.read_index(
                str(index_path)
            )

            chunk_payload = json.loads(
                chunks_path.read_text(
                    encoding="utf-8"
                )
            )

            chunks = [
                self._deserialize_chunk(item)
                for item in chunk_payload
            ]
        except (
            OSError,
            RuntimeError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
        ) as error:
            raise VectorStoreError(
                message=(
                    "저장된 FAISS 인덱스를 "
                    "불러오지 못했습니다."
                ),
            ) from error

        if int(index.ntotal) != len(chunks):
            raise VectorStoreErr