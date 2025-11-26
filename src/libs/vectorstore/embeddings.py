"""Embedding providers for vector search."""

from abc import ABC, abstractmethod

from chromadb import Documents, EmbeddingFunction, Embeddings

from ..config import VectorConfig
from ..exceptions import (
    EmbeddingAPIError,
    EmbeddingConnectionError,
    EmbeddingProviderError,
    EmbeddingTimeoutError,
)


class BaseEmbeddingProvider(EmbeddingFunction, ABC):
    """Base class for embedding providers."""

    @abstractmethod
    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Convert texts to embedding vectors.

        Args:
            documents: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        pass

    def embed_query(self, query: str) -> list[float]:
        """Convert a single query to embedding vector.

        Args:
            query: Query text to embed.

        Returns:
            Embedding vector.
        """
        result = self.embed_documents([query])
        return result[0] if result else []

    def __call__(self, input: Documents) -> Embeddings:
        """ChromaDB compatibility - delegates to embed_documents."""
        return self.embed_documents(list(input))

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimension."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass


class DefaultEmbeddingProvider(BaseEmbeddingProvider):
    """Default embedding provider using ChromaDB's built-in all-MiniLM-L6-v2."""

    def __init__(self) -> None:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

        self._ef = DefaultEmbeddingFunction()

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Convert texts to embedding vectors."""
        if not documents:
            return []
        return self._ef(documents)

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return 384

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "default"


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider using Ollama local models."""

    def __init__(self, host: str, model: str) -> None:
        self._host = host
        self._model = model
        self._dimension: int | None = None

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Convert texts to embedding vectors."""
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
                    if self._dimension is None and embedding:
                        self._dimension = len(embedding)
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

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimension or 768

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "ollama"


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider using OpenAI API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Convert texts to embedding vectors."""
        if not documents:
            return []

        try:
            from openai import OpenAI
        except ImportError:
            raise EmbeddingProviderError(
                "openai package not installed. Install with: pip install 'py-obsidian-tools[vector-openai]'"
            )

        try:
            client = OpenAI(api_key=self._api_key)
            response = client.embeddings.create(input=documents, model=self._model)
            return [item.embedding for item in response.data]
        except ImportError:
            raise
        except Exception as e:
            raise EmbeddingAPIError(f"OpenAI API error: {e}") from e

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimensions.get(self._model, 1536)

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "openai"


class GoogleEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider using Google Generative AI API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Convert texts to embedding vectors."""
        if not documents:
            return []

        try:
            import google.generativeai as genai
        except ImportError:
            raise EmbeddingProviderError(
                "google-generativeai package not installed. Install with: pip install 'py-obsidian-tools[vector-google]'"
            )

        try:
            genai.configure(api_key=self._api_key)
            embeddings: list[list[float]] = []
            for text in documents:
                result = genai.embed_content(
                    model=f"models/{self._model}",
                    content=text,
                    task_type="retrieval_document",
                )
                embeddings.append(result["embedding"])
            return embeddings
        except ImportError:
            raise
        except Exception as e:
            raise EmbeddingAPIError(f"Google AI API error: {e}") from e

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return 768

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "google"


class CohereEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider using Cohere API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Convert texts to embedding vectors."""
        if not documents:
            return []

        try:
            import cohere
        except ImportError:
            raise EmbeddingProviderError(
                "cohere package not installed. Install with: pip install 'py-obsidian-tools[vector-cohere]'"
            )

        try:
            client = cohere.Client(self._api_key)
            response = client.embed(
                texts=documents,
                model=self._model,
                input_type="search_document",
            )
            return [list(emb) for emb in response.embeddings]
        except ImportError:
            raise
        except Exception as e:
            raise EmbeddingAPIError(f"Cohere API error: {e}") from e

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return 1024

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "cohere"


def get_embedding_provider(config: VectorConfig) -> BaseEmbeddingProvider:
    """Factory function to create embedding provider based on config."""
    provider = config.provider

    if provider == "default":
        return DefaultEmbeddingProvider()
    elif provider == "ollama":
        return OllamaEmbeddingProvider(
            host=config.ollama_host,
            model=config.ollama_model,
        )
    elif provider == "openai":
        if not config.openai_api_key:
            raise EmbeddingProviderError("OpenAI API key is required")
        return OpenAIEmbeddingProvider(
            api_key=config.openai_api_key,
            model=config.openai_model,
        )
    elif provider == "google":
        if not config.google_api_key:
            raise EmbeddingProviderError("Google API key is required")
        return GoogleEmbeddingProvider(
            api_key=config.google_api_key,
            model=config.google_model,
        )
    elif provider == "cohere":
        if not config.cohere_api_key:
            raise EmbeddingProviderError("Cohere API key is required")
        return CohereEmbeddingProvider(
            api_key=config.cohere_api_key,
            model=config.cohere_model,
        )
    else:
        raise EmbeddingProviderError(f"Unknown provider: {provider}")
