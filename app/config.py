from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Agentic AI for Regulatory Compliance Automation")
    app_env: str = Field(default="dev")
    app_host: str = Field(default="127.0.0.1")
    app_port: int = Field(default=8000)
    log_level: str = Field(default="INFO")

    llm_mode: str = Field(default="mock")
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4.1-mini")

    vector_backend: str = Field(default="chroma")
    chroma_path: str = Field(default="./storage/chroma")
    collection_name: str = Field(default="financial_regulations")

    audit_store_path: str = Field(default="./storage/audits")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def chroma_dir(self) -> Path:
        path = Path(self.chroma_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def audit_store_dir(self) -> Path:
        path = Path(self.audit_store_path)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
