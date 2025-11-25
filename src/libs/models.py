"""Pydantic models for Obsidian Local REST API."""

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
