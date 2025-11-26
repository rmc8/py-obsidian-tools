"""Configuration management using Pydantic Settings."""

from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ObsidianConfigError, VectorConfigError


class ObsidianConfig(BaseSettings):
    """Configuration for Obsidian Local REST API connection."""

    model_config = SettingsConfigDict(
        env_prefix="OBSIDIAN_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str = Field(
        default="",
        description="API key from Obsidian Local REST API plugin",
    )
    host: str = Field(
        default="localhost",
        description="Obsidian Local REST API host",
    )
    port: int = Field(
        default=27124,
        ge=1,
        le=65535,
        description="Obsidian Local REST API port",
    )
    protocol: str = Field(
        default="https",
        description="Protocol (http or https)",
    )

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v: str) -> str:
        """Validate that protocol is http or https."""
        if v.lower() not in ("http", "https"):
            raise ValueError("Protocol must be 'http' or 'https'")
        return v.lower()

    @property
    def base_url(self) -> str:
        """Build the base URL for API requests."""
        return f"{self.protocol}://{self.host}:{self.port}"

    def validate_config(self) -> None:
        """Validate that required configuration is present."""
        if not self.api_key:
            raise ObsidianConfigError(
                "OBSIDIAN_API_KEY is not set. "
                "Get your API key from Obsidian Settings > Local REST API > Security"
            )


def load_config() -> ObsidianConfig:
    """Load and return the Obsidian configuration."""
    return ObsidianConfig()


class VectorConfig(BaseSettings):
    """Configuration for vector search functionality."""

    model_config = SettingsConfigDict(
        env_prefix="VECTOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ChromaDB settings
    chroma_path: str = Field(
        default=".chroma",
        description="Path to ChromaDB storage directory",
    )
    collection_name: str = Field(
        default="obsidian_notes",
        description="Name of the ChromaDB collection",
    )

    # Chunking settings
    chunk_size: int = Field(
        default=512,
        ge=100,
        le=4000,
        description="Maximum chunk size in characters",
    )

    # Batch processing settings
    batch_size: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of notes to process in parallel for external API providers",
    )

    # Embedding provider settings
    provider: Literal["default", "ollama", "openai", "google", "cohere"] = Field(
        default="default",
        description="Embedding provider to use",
    )

    # Ollama settings
    ollama_host: str = Field(
        default="http://localhost:11434",
        description="Ollama server host URL",
    )
    ollama_model: str = Field(
        default="nomic-embed-text",
        description="Ollama embedding model name",
    )

    # OpenAI settings
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for embeddings",
    )
    openai_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model name",
    )

    # Google settings
    google_api_key: str | None = Field(
        default=None,
        description="Google AI API key for embeddings",
    )
    google_model: str = Field(
        default="embedding-001",
        description="Google embedding model name",
    )

    # Cohere settings
    cohere_api_key: str | None = Field(
        default=None,
        description="Cohere API key for embeddings",
    )
    cohere_model: str = Field(
        default="embed-multilingual-v3.0",
        description="Cohere embedding model name",
    )

    @model_validator(mode="after")
    def validate_provider_api_keys(self) -> "VectorConfig":
        """Validate that required API keys are present for external providers."""
        if self.provider == "openai" and not self.openai_api_key:
            raise VectorConfigError(
                "VECTOR_OPENAI_API_KEY is required when using OpenAI provider"
            )
        if self.provider == "google" and not self.google_api_key:
            raise VectorConfigError(
                "VECTOR_GOOGLE_API_KEY is required when using Google provider"
            )
        if self.provider == "cohere" and not self.cohere_api_key:
            raise VectorConfigError(
                "VECTOR_COHERE_API_KEY is required when using Cohere provider"
            )
        return self


def load_vector_config() -> VectorConfig:
    """Load and return the vector search configuration."""
    return VectorConfig()
