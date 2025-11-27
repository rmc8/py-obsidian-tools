"""Embedding providers for vector search using ChromaDB's official functions."""

from typing import Protocol

from chromadb import Documents, EmbeddingFunction, Embeddings

from ..config import VectorConfig
from ..exceptions import (
    EmbeddingAPIError,
    EmbeddingConnectionError,
    EmbeddingProviderError,
    EmbeddingTimeoutError,
)


class EmbeddingProviderProtocol(Protocol):
    """Protocol for embedding providers with name and dimension."""

    def __call__(self, input: Documents) -> Embeddings: ...

    def name(self) -> str: ...

    def dimension(self) -> int: ...


class EmbeddingProviderWrapper(EmbeddingFunction):
    """Wrapper for ChromaDB's official EmbeddingFunction with name/dimension support.

    Inherits from EmbeddingFunction to ensure full compatibility with ChromaDB's
    collection.query() which expects embed_query method.
    """

    def __init__(
        self,
        ef: EmbeddingFunction,
        provider_name: str,
        embedding_dimension: int,
    ) -> None:
        """Initialize the wrapper.

        Args:
            ef: ChromaDB EmbeddingFunction instance.
            provider_name: Name of the provider (e.g., "openai", "default").
            embedding_dimension: Dimension of the embedding vectors.
        """
        self._ef = ef
        self._name = provider_name
        self._dimension = embedding_dimension

    def __call__(self, input: Documents) -> Embeddings:
        """Generate embeddings using the wrapped function."""
        return self._ef(input)

    def embed_query(self, input: Documents) -> Embeddings:
        """Embed query documents for search.

        ChromaDB's collection.query() calls this method with query_texts as a list.

        Args:
            input: List of query texts to embed.

        Returns:
            List of embedding vectors.
        """
        return self._ef(input)

    def name(self) -> str:
        """Return the provider name."""
        return self._name

    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimension


class OllamaEmbeddingProvider:
    """Custom embedding provider using Ollama local models.

    Note: ChromaDB doesn't have an official Ollama EmbeddingFunction,
    so we maintain a custom implementation.
    """

    def __init__(self, host: str, model: str) -> None:
        self._host = host
        self._model = model
        self._dimension_cache: int | None = None

    def __call__(self, input: Documents) -> Embeddings:
        """Generate embeddings for the input documents."""
        documents = list(input)
        if not documents:
            return []

        import httpx

        embeddings: list[list[float]] = []
        try:
            with httpx.Client(timeout=60.0) as client:
                for text in documents:
                    response = client.post(
                        f"{self._host}/api/embeddings",
                        json={"model": self._model, "prompt": text},
                    )
                    response.raise_for_status()
                    data = response.json()
                    embedding = data.get("embedding", [])
                    embeddings.append(embedding)
                    if self._dimension_cache is None and embedding:
                        self._dimension_cache = len(embedding)
        except httpx.ConnectError as e:
            raise EmbeddingConnectionError(
                f"Cannot connect to Ollama at {self._host}: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise EmbeddingTimeoutError(f"Ollama request timed out: {e}") from e
        except httpx.HTTPStatusError as e:
            raise EmbeddingAPIError(f"Ollama HTTP error: {e}") from e
        except httpx.HTTPError as e:
            raise EmbeddingProviderError(f"Ollama API error: {e}") from e
        return embeddings

    def name(self) -> str:
        """Return the provider name."""
        return "ollama"

    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimension_cache or 768


def get_embedding_provider(
    config: VectorConfig,
) -> EmbeddingProviderWrapper | OllamaEmbeddingProvider:
    """Factory function to create embedding provider based on config.

    Uses ChromaDB's official EmbeddingFunction implementations where available.

    Args:
        config: Vector search configuration.

    Returns:
        Embedding provider instance.

    Raises:
        EmbeddingProviderError: If provider is unknown or required keys are missing.
    """
    provider = config.provider

    if provider == "default":
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

        return EmbeddingProviderWrapper(
            ef=DefaultEmbeddingFunction(),
            provider_name="default",
            embedding_dimension=384,
        )

    elif provider == "ollama":
        # ChromaDB doesn't have official Ollama support
        return OllamaEmbeddingProvider(
            host=config.ollama_host,
            model=config.ollama_model,
        )

    elif provider == "openai":
        if not config.openai_api_key:
            raise EmbeddingProviderError("OpenAI API key is required")

        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        return EmbeddingProviderWrapper(
            ef=OpenAIEmbeddingFunction(
                api_key=config.openai_api_key,
                model_name=config.openai_model,
            ),
            provider_name="openai",
            embedding_dimension=dimensions.get(config.openai_model, 1536),
        )

    elif provider == "google":
        if not config.google_api_key:
            raise EmbeddingProviderError("Google API key is required")

        try:
            from chromadb.utils.embedding_functions import (
                GoogleGenerativeAiEmbeddingFunction,
            )

            return EmbeddingProviderWrapper(
                ef=GoogleGenerativeAiEmbeddingFunction(
                    api_key=config.google_api_key,
                    model_name=config.google_model,
                ),
                provider_name="google",
                embedding_dimension=768,
            )
        except ImportError:
            raise EmbeddingProviderError(
                "google-generativeai package not installed. "
                "Install with: pip install 'py-obsidian-tools[vector-google]'"
            )

    elif provider == "cohere":
        if not config.cohere_api_key:
            raise EmbeddingProviderError("Cohere API key is required")

        try:
            from chromadb.utils.embedding_functions import CohereEmbeddingFunction

            return EmbeddingProviderWrapper(
                ef=CohereEmbeddingFunction(
                    api_key=config.cohere_api_key,
                    model_name=config.cohere_model,
                ),
                provider_name="cohere",
                embedding_dimension=1024,
            )
        except ImportError:
            raise EmbeddingProviderError(
                "cohere package not installed. "
                "Install with: pip install 'py-obsidian-tools[vector-cohere]'"
            )

    else:
        raise EmbeddingProviderError(f"Unknown provider: {provider}")
