"""Custom exception hierarchy for Obsidian API errors."""


class ObsidianAPIError(Exception):
    """Base exception for Obsidian API errors."""

    pass


class ObsidianNotFoundError(ObsidianAPIError):
    """Resource not found (HTTP 404)."""

    pass


class ObsidianAuthError(ObsidianAPIError):
    """Authentication failed (HTTP 401/403)."""

    pass


class ObsidianConnectionError(ObsidianAPIError):
    """Network connection issues."""

    pass


class ObsidianTimeoutError(ObsidianAPIError):
    """Timeout error when communicating with Obsidian API."""

    pass


class ObsidianRateLimitError(ObsidianAPIError):
    """Rate limit exceeded (HTTP 429)."""

    pass


class ObsidianConfigError(ObsidianAPIError):
    """Configuration errors (missing or invalid settings)."""

    pass


# Vector search exceptions


class VectorStoreError(Exception):
    """Base exception for vector store errors."""

    pass


class IndexNotFoundError(VectorStoreError):
    """Vector index not found or not initialized."""

    pass


class EmbeddingProviderError(VectorStoreError):
    """Base exception for embedding provider errors."""

    pass


class EmbeddingConnectionError(EmbeddingProviderError):
    """Cannot connect to embedding provider service."""

    pass


class EmbeddingTimeoutError(EmbeddingProviderError):
    """Embedding API request timed out."""

    pass


class EmbeddingAPIError(EmbeddingProviderError):
    """Embedding API returned an error response."""

    pass


class VectorConfigError(VectorStoreError):
    """Vector search configuration errors."""

    pass
