"""Vector search functionality for py-obsidian-tools using ChromaDB."""

from .chunker import MarkdownChunker
from .embeddings import (
    EmbeddingProviderProtocol,
    EmbeddingProviderWrapper,
    OllamaEmbeddingProvider,
    get_embedding_provider,
)
from .store import ObsidianVectorStore

__all__ = [
    "MarkdownChunker",
    "EmbeddingProviderProtocol",
    "EmbeddingProviderWrapper",
    "OllamaEmbeddingProvider",
    "get_embedding_provider",
    "ObsidianVectorStore",
]
