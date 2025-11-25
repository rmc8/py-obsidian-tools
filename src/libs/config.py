"""Configuration management using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ObsidianConfigError


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
        default=27123,
        description="Obsidian Local REST API port",
    )
    protocol: str = Field(
        default="http",
        description="Protocol (http or https)",
    )

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
