from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Personal Knowledge RAG Chatbot"
    app_env: Literal["local", "test", "production"] = "local"
    log_level: str = "INFO"

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    raw_document_path: Path = Path("data/raw")
    vector_store_path: Path = Path("data/vector_store")
    vector_index_name: str = "personal_knowledge_v1"

    chunk_size: int = Field(default=1000, gt=0)
    chunk_overlap: int = Field(default=150, ge=0)
    search_top_k: int = Field(default=5, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()