from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class IndexingResult:
    document_count: int
    chunk_count: int
    vector_dimension: int