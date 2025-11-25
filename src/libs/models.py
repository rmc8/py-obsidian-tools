"""Pydantic models for Obsidian Local REST API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """Information about a file in the vault."""

    path: str = Field(..., description="File path relative to vault root")


class NoteContent(BaseModel):
    """Note content with optional frontmatter."""

    content: str = Field(default="", description="Note content (markdown)")
    frontmatter: dict[str, Any] | None = Field(
        default=None, description="YAML frontmatter as dictionary"
    )
    tags: list[str] = Field(default_factory=list, description="Tags in the note")
    stat: dict[str, Any] | None = Field(
        default=None, description="File statistics (ctime, mtime, size)"
    )
    path: str | None = Field(default=None, description="File path")


class SearchMatch(BaseModel):
    """A single match within a search result."""

    match: str = Field(..., description="The matched text")
    context: str = Field(default="", description="Surrounding context")


class SearchResult(BaseModel):
    """Search result for a single file."""

    filename: str = Field(..., description="Path to the matching file")
    matches: list[SearchMatch] = Field(
        default_factory=list, description="List of matches in this file"
    )
    score: float | None = Field(default=None, description="Relevance score")


class CommandInfo(BaseModel):
    """Information about an Obsidian command."""

    id: str = Field(..., description="Command ID")
    name: str = Field(..., description="Human-readable command name")


class VaultInfo(BaseModel):
    """Information about files in the vault."""

    files: list[str] = Field(default_factory=list, description="List of file paths")


# Vector search models


class NoteChunk(BaseModel):
    """Metadata for a note chunk stored in ChromaDB."""

    path: str = Field(..., description="Note path (e.g., 'Projects/MyProject.md')")
    folder: str = Field(..., description="Parent folder (e.g., 'Projects')")
    title: str = Field(..., description="Note title (e.g., 'MyProject')")
    mtime: float = Field(..., description="Last modified time (Unix timestamp)")
    chunk_index: int = Field(..., ge=0, description="Chunk number (0-indexed)")
    total_chunks: int = Field(..., ge=1, description="Total chunks in note")


class VectorSearchResult(BaseModel):
    """A single result from vector search."""

    path: str = Field(..., description="Note path")
    title: str = Field(..., description="Note title")
    folder: str = Field(..., description="Parent folder")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")
    content_preview: str = Field(
        ..., max_length=200, description="Content preview (max 200 chars)"
    )
    chunk_index: int = Field(..., ge=0, description="Chunk number")
    total_chunks: int = Field(..., ge=1, description="Total chunks in note")


class IndexStatus(BaseModel):
    """Status of the vector search index."""

    collection_name: str = Field(..., description="ChromaDB collection name")
    total_documents: int = Field(..., ge=0, description="Total chunks indexed")
    total_notes: int = Field(..., ge=0, description="Total notes indexed")
    embedding_provider: str = Field(..., description="Active embedding provider")
    embedding_dimension: int = Field(..., gt=0, description="Embedding dimension")
    last_updated: datetime | None = Field(
        default=None, description="Last index update time"
    )
    chroma_path: str = Field(..., description="ChromaDB storage path")
