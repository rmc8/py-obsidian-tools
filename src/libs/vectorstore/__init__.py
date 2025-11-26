"""Vector search functionality for py-obsidian-tools using ChromaDB."""

from .chunker import MarkdownChunker
from .embeddings import (BaseEmbeddingProvider, CohereEmbeddingProvider,
                         DefaultEmbeddingProvider, GoogleEmbeddingProvider,
                         OllamaEmbeddingProvider, OpenAIEmbeddingProvider,
                         get_embedding_provider)
from .store import ObsidianVectorStore

__all__ = [
    "MarkdownChunker",
    "BaseEmbeddingProvider",
    "DefaultEmbeddingProvider",
    "OllamaEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "GoogleEmbeddingProvider",
    "CohereEmbeddingProvider",
    "get_embedding_provider",
    "ObsidianVectorStore",
]
