"""Markdown chunking using semantic-text-splitter."""

from semantic_text_splitter import MarkdownSplitter


class MarkdownChunker:
    """Chunker for Markdown content using semantic-text-splitter."""

    def __init__(self, chunk_size: int = 512) -> None:
        """Initialize the chunker.

        Args:
            chunk_size: Maximum chunk size in characters.
        """
        self._chunk_size = chunk_size
        self._splitter = MarkdownSplitter(chunk_size)

    def chunk(self, content: str) -> list[str]:
        """Split markdown content into chunks.

        Args:
            content: Markdown content to split.

        Returns:
            List of text chunks.
        """
        if not content or not content.strip():
            return []

        chunks = self._splitter.chunks(content)
        return [c for c in chunks if c.strip()]

    @property
    def chunk_size(self) -> int:
        """Return the configured chunk size."""
        return self._chunk_size
