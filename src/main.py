"""MCP server for Obsidian via Local REST API."""

import functools
import json
from contextvars import ContextVar
from typing import Callable, ParamSpec, TypeVar

from mcp.server.fastmcp import FastMCP

from .libs import ObsidianAPIError, ObsidianClient, ObsidianConfigError, load_config
from .libs.config import load_vector_config
from .libs.exceptions import IndexNotFoundError, VectorConfigError, VectorStoreError
from .libs.utils import (
    format_frontmatter,
    json_error,
    validate_patch_params,
    validate_period,
)

# Initialize FastMCP server
mcp = FastMCP("obsidian")

# Load configuration (lazy validation)
_config = None

# Context variable for client injection
_client_ctx: ContextVar[ObsidianClient] = ContextVar("obsidian_client")

P = ParamSpec("P")
T = TypeVar("T")


def get_config():
    """Get configuration, validating on first access."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def get_client() -> ObsidianClient:
    """Get the current ObsidianClient from context."""
    return _client_ctx.get()


def handle_obsidian_errors(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator to handle ObsidianConfigError and ObsidianAPIError."""

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except ObsidianConfigError as e:
            return f"Configuration Error: {e}"
        except ObsidianAPIError as e:
            return f"Error: {e}"

    return wrapper


def with_client(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator to inject configured ObsidianClient via context variable."""

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        config = get_config()
        config.validate_config()
        async with ObsidianClient(config) as client:
            token = _client_ctx.set(client)
            try:
                return await func(*args, **kwargs)
            finally:
                _client_ctx.reset(token)

    return wrapper


# ============================================================
# Tier 1: Basic Operations
# ============================================================


@mcp.tool()
@handle_obsidian_errors
@with_client
async def list_notes(directory: str = "") -> str:
    """List all notes in the vault or a specific directory.

    Args:
        directory: Optional subdirectory path (e.g., "daily/2024" or "projects").
                   Leave empty to list all files in the vault root.

    Returns:
        A formatted list of note paths, one per line.
    """
    client = get_client()
    files = await client.list_files(directory)

    if not files:
        location = f"'{directory}'" if directory else "vault"
        return f"No files found in {location}."

    # Format output
    result = [f"Found {len(files)} file(s):"]
    for f in sorted(files):
        result.append(f"  - {f}")
    return "\n".join(result)


@mcp.tool()
@handle_obsidian_errors
@with_client
async def read_note(path: str) -> str:
    """Read the content of a specific note.

    Args:
        path: Relative path from vault root (e.g., "daily/2024-01-15.md" or "README.md")

    Returns:
        The note content including frontmatter if present.
    """
    client = get_client()
    note = await client.get_note(path)

    result_parts = []

    # Add frontmatter if present
    if note.frontmatter:
        result_parts.append(format_frontmatter(note.frontmatter))

    # Add content
    if note.content:
        result_parts.append(note.content)

    return "\n".join(result_parts) if result_parts else "(empty note)"


@mcp.tool()
@handle_obsidian_errors
@with_client
async def search_notes(query: str, context_length: int = 100) -> str:
    """Search for notes containing specific text.

    Args:
        query: The search query (text to find)
        context_length: Number of characters of context around matches (default: 100)

    Returns:
        Search results with matching files and context.
    """
    client = get_client()
    results = await client.search_simple(query, context_length)

    if not results:
        return f"No results found for '{query}'."

    output = [f"Found matches in {len(results)} file(s) for '{query}':\n"]

    for result in results:
        output.append(f"## {result.filename}")
        if result.matches:
            for match in result.matches[:3]:  # Limit to 3 matches per file
                context = match.context.strip()
                if context:
                    output.append(f"  ...{context}...")
        output.append("")

    return "\n".join(output)


@mcp.tool()
@handle_obsidian_errors
@with_client
async def create_note(
    path: str,
    content: str,
    frontmatter: str = "",
) -> str:
    """Create a new note or overwrite an existing one.

    Args:
        path: Path for the new note (e.g., "notes/my-note.md")
        content: The markdown content for the note
        frontmatter: Optional YAML frontmatter as JSON string
                     (e.g., '{"title": "My Note", "tags": ["tag1", "tag2"]}')

    Returns:
        Success or error message.
    """
    client = get_client()
    # Build full content with frontmatter
    full_content_parts = []

    if frontmatter:
        try:
            fm_dict = json.loads(frontmatter)
            if fm_dict:
                full_content_parts.append(format_frontmatter(fm_dict))
        except json.JSONDecodeError:
            return "Error: Invalid frontmatter JSON format."

    full_content_parts.append(content)
    full_content = "\n".join(full_content_parts)

    await client.create_note(path, full_content)
    return f"Successfully created note: {path}"


# ============================================================
# Tier 2: CRUD Completion
# ============================================================


@mcp.tool()
@handle_obsidian_errors
@with_client
async def update_note(path: str, content: str) -> str:
    """Update (replace) the entire content of an existing note.

    Args:
        path: Path to the note to update
        content: New content (will replace existing content entirely)

    Returns:
        Success or error message.
    """
    client = get_client()
    await client.update_note(path, content)
    return f"Successfully updated note: {path}"


@mcp.tool()
@handle_obsidian_errors
@with_client
async def append_note(path: str, content: str) -> str:
    """Append content to the end of an existing note.

    Args:
        path: Path to the note
        content: Content to append

    Returns:
        Success or error message.
    """
    client = get_client()
    await client.append_note(path, content)
    return f"Successfully appended to note: {path}"


@mcp.tool()
@handle_obsidian_errors
@with_client
async def delete_note(path: str, confirm: bool = False) -> str:
    """Delete a note from the vault.

    Args:
        path: Path to the note to delete
        confirm: Must be True to actually delete (safety check)

    Returns:
        Success or error message.
    """
    client = get_client()
    if not confirm:
        return "Error: Set confirm=True to delete the note. This is a safety check."

    await client.delete_note(path)
    return f"Successfully deleted note: {path}"


# ============================================================
# Tier 3: Advanced Operations
# ============================================================


@mcp.tool()
@handle_obsidian_errors
@with_client
async def patch_note(
    path: str,
    content: str,
    target_type: str,
    target: str,
    operation: str = "replace",
) -> str:
    """Update a specific section of a note.

    Args:
        path: Path to the note
        content: New content for the section
        target_type: Type of target - "heading", "block", or "frontmatter"
        target: Target identifier:
                - For "heading": The heading text WITHOUT # markers (e.g., "My Section")
                  For nested headings, use "::" delimiter (e.g., "Parent::Child")
                - For "block": The block ID (e.g., "^block-id")
                - For "frontmatter": The field name (e.g., "tags")
        operation: "append", "prepend", or "replace" (default: "replace")

    Returns:
        Success or error message.
    """
    client = get_client()
    if error := validate_patch_params(target_type, operation):
        return error

    await client.patch_note(path, content, target_type, target, operation)
    return f"Successfully patched note: {path} ({target_type}: {target})"


@mcp.tool()
@handle_obsidian_errors
@with_client
async def list_commands() -> str:
    """List all available Obsidian commands.

    Returns:
        A list of available commands with their IDs and names.
    """
    client = get_client()
    commands = await client.list_commands()

    if not commands:
        return "No commands available."

    output = [f"Available commands ({len(commands)}):"]
    for cmd in sorted(commands, key=lambda c: c.name):
        output.append(f"  - {cmd.name}")
        output.append(f"    ID: {cmd.id}")
    return "\n".join(output)


@mcp.tool()
@handle_obsidian_errors
@with_client
async def execute_command(command_id: str) -> str:
    """Execute an Obsidian command.

    Args:
        command_id: The command ID to execute (use list_commands to find IDs)

    Returns:
        Success or error message.
    """
    client = get_client()
    await client.execute_command(command_id)
    return f"Successfully executed command: {command_id}"


# ============================================================
# Tier 4: Additional Operations
# ============================================================


@mcp.tool()
@handle_obsidian_errors
@with_client
async def batch_read_notes(paths: str) -> str:
    """Read multiple notes at once.

    Args:
        paths: Comma-separated list of note paths (e.g., "note1.md,folder/note2.md")

    Returns:
        Contents of all notes with headers.
    """
    client = get_client()
    path_list = [p.strip() for p in paths.split(",") if p.strip()]
    if not path_list:
        return "Error: No paths provided."

    results = []
    for path in path_list:
        try:
            note = await client.get_note(path)
            content_parts = [f"# {path}\n"]
            if note.frontmatter:
                content_parts.append(format_frontmatter(note.frontmatter))
            if note.content:
                content_parts.append(note.content)
            results.append("\n".join(content_parts))
        except ObsidianAPIError as e:
            results.append(f"# {path}\n\nError reading file: {e}")

    return "\n\n---\n\n".join(results)


@mcp.tool()
@handle_obsidian_errors
@with_client
async def complex_search(query: str) -> str:
    """Search for notes using JsonLogic query.

    Args:
        query: JsonLogic query as JSON string.
               Examples:
               - Find all markdown files: {"glob": ["*.md", {"var": "path"}]}
               - Find files with tag: {"in": ["myTag", {"var": "tags"}]}
               - Find by frontmatter: {"==": [{"var": "frontmatter.status"}, "done"]}
               - Combined: {"and": [{"glob": ["*.md", {"var": "path"}]},
                                   {"regexp": [".*Work.*", {"var": "path"}]}]}

    Returns:
        Search results with matching files.
    """
    client = get_client()
    try:
        query_dict = json.loads(query)
    except json.JSONDecodeError:
        return "Error: Invalid JSON query format."

    results = await client.search_jsonlogic(query_dict)

    if not results:
        return "No results found."

    output = [f"Found {len(results)} matching file(s):\n"]
    for result in results[:50]:  # Limit to 50 results
        filename = result.get("filename", "Unknown")
        output.append(f"  - {filename}")

    return "\n".join(output)


@mcp.tool()
@handle_obsidian_errors
@with_client
async def dataview_query(dql: str) -> str:
    """Execute a Dataview Query Language (DQL) query.

    Args:
        dql: Dataview Query Language string.
             Examples:
             - List all files: "LIST"
             - Table with columns: "TABLE file.mtime, file.size SORT file.mtime DESC"
             - Filter by tag: "LIST FROM #project"
             - Filter by folder: "LIST FROM \"Projects\""
             - Recent files: "TABLE file.mtime WHERE file.mtime >= date(today) - dur(7 days)"

    Returns:
        Query results as formatted text.

    Note:
        Requires the Dataview plugin to be installed in Obsidian.
    """
    client = get_client()
    results = await client.search_dataview(dql)

    if not results:
        return "No results found."

    output = [f"Query results ({len(results)} items):\n"]
    for i, result in enumerate(results[:100], 1):  # Limit to 100 results
        if isinstance(result, dict):
            filename = result.get("filename", f"Item {i}")
            output.append(f"  {i}. {filename}")
            # Show additional fields
            for key, value in result.items():
                if key not in ("filename", "file"):
                    output.append(f"      {key}: {value}")
        else:
            output.append(f"  {i}. {result}")

    return "\n".join(output)


@mcp.tool()
@handle_obsidian_errors
@with_client
async def get_recent_changes(limit: int = 10, days: int = 90) -> str:
    """Get recently modified files in the vault.

    Args:
        limit: Maximum number of files to return (default: 10, max: 100)
        days: Only include files modified within this many days (default: 90)

    Returns:
        List of recently modified files with modification times.

    Note:
        Requires the Dataview plugin to be installed in Obsidian.
    """
    client = get_client()
    limit = min(max(1, limit), 100)
    days = max(1, days)

    results = await client.get_recent_changes(limit, days)

    if not results:
        return f"No files modified in the last {days} days."

    output = [f"Recently modified files (last {days} days):\n"]
    for result in results:
        filename = result.get("filename", "Unknown")
        mtime = result.get("result", {})
        output.append(f"  - {filename}")
        if isinstance(mtime, dict) and "file.mtime" in mtime:
            output.append(f"    Modified: {mtime['file.mtime']}")

    return "\n".join(output)


@mcp.tool()
@handle_obsidian_errors
@with_client
async def get_periodic_note(
    period: str,
    include_metadata: bool = False,
) -> str:
    """Get the current periodic note for the specified period.

    Args:
        period: Period type - "daily", "weekly", "monthly", "quarterly", or "yearly"
        include_metadata: If True, include frontmatter and metadata

    Returns:
        Content of the periodic note.

    Note:
        Requires the Periodic Notes plugin to be installed in Obsidian.
    """
    client = get_client()
    if error := validate_period(period):
        return error

    result = await client.get_periodic_note(period, include_metadata)

    if isinstance(result, str):
        return result if result else f"No {period} note found."

    # NoteContent object
    result_parts = []
    if result.frontmatter:
        result_parts.append(format_frontmatter(result.frontmatter))

    if result.content:
        result_parts.append(result.content)

    return "\n".join(result_parts) if result_parts else f"No {period} note found."


# NOTE: Disabled due to Dataview query pattern matching issues
# @mcp.tool()
# @handle_obsidian_errors
# @with_client
# async def get_recent_periodic_notes(
#     period: str,
#     limit: int = 5,
#     include_content: bool = False,
# ) -> str:
#     """Get recent periodic notes for the specified period type.
#
#     Args:
#         period: Period type - "daily", "weekly", "monthly", "quarterly", or "yearly"
#         limit: Maximum number of notes to return (1-50, default: 5)
#         include_content: Whether to include note content (default: False)
#
#     Returns:
#         List of recent periodic notes.
#
#     Note:
#         Requires the Dataview plugin to be installed in Obsidian.
#         Uses date patterns to identify periodic notes (e.g., YYYY-MM-DD for daily).
#     """
#     client = get_client()
#     if error := validate_period(period):
#         return error
#
#     limit = min(max(1, limit), 50)
#
#     results = await client.get_recent_periodic_notes(period, limit, include_content)
#
#     if not results:
#         return f"No recent {period} notes found."
#
#     output = [f"Recent {period} notes ({len(results)}):\n"]
#     for note in results:
#         if isinstance(note, dict):
#             path = note.get("path", note.get("filename", "Unknown"))
#             output.append(f"  - {path}")
#             if include_content and "content" in note:
#                 output.append(f"    Content preview: {note['content'][:100]}...")
#         else:
#             output.append(f"  - {note}")
#
#     return "\n".join(output)


@mcp.tool()
@handle_obsidian_errors
@with_client
async def open_note(path: str, new_leaf: bool = False) -> str:
    """Open a note in Obsidian's UI.

    Args:
        path: Path to the note to open
        new_leaf: Whether to open in a new tab (default: False)

    Returns:
        Success or error message.
    """
    client = get_client()
    await client.open_file(path, new_leaf)
    return f"Successfully opened note: {path}"


@mcp.tool()
@handle_obsidian_errors
@with_client
async def get_active_note() -> str:
    """Get the currently active note in Obsidian.

    Returns:
        Content of the active note, or error if no note is active.
    """
    client = get_client()
    note = await client.get_active_file()

    if note is None:
        return "No active note in Obsidian."

    result_parts = []
    if note.path:
        result_parts.append(f"Path: {note.path}\n")

    if note.frontmatter:
        result_parts.append(format_frontmatter(note.frontmatter))

    if note.content:
        result_parts.append(note.content)

    return "\n".join(result_parts) if result_parts else "(empty note)"


@mcp.tool()
@handle_obsidian_errors
@with_client
async def update_active_note(content: str) -> str:
    """Update (replace) the content of the currently active note.

    Args:
        content: New content for the note (will replace existing content)

    Returns:
        Success or error message.
    """
    client = get_client()
    await client.update_active_file(content)
    return "Successfully updated active note."


@mcp.tool()
@handle_obsidian_errors
@with_client
async def append_active_note(content: str) -> str:
    """Append content to the currently active note.

    Args:
        content: Content to append to the note

    Returns:
        Success or error message.
    """
    client = get_client()
    await client.append_active_file(content)
    return "Successfully appended to active note."


@mcp.tool()
@handle_obsidian_errors
@with_client
async def patch_active_note(
    content: str,
    target_type: str,
    target: str,
    operation: str = "replace",
) -> str:
    """Update a specific section of the currently active note.

    Args:
        content: New content for the section
        target_type: Type of target - "heading", "block", or "frontmatter"
        target: Target identifier:
                - For "heading": The heading text WITHOUT # markers (e.g., "My Section")
                  For nested headings, use "::" delimiter (e.g., "Parent::Child")
                - For "block": The block ID (e.g., "^block-id")
                - For "frontmatter": The field name (e.g., "tags")
        operation: "append", "prepend", or "replace" (default: "replace")

    Returns:
        Success or error message.
    """
    client = get_client()
    if error := validate_patch_params(target_type, operation):
        return error

    await client.patch_active_file(content, target_type, target, operation)
    return f"Successfully patched active note ({target_type}: {target})"


@mcp.tool()
@handle_obsidian_errors
@with_client
async def delete_active_note(confirm: bool = False) -> str:
    """Delete the currently active note in Obsidian.

    Args:
        confirm: Must be True to actually delete (safety check)

    Returns:
        Success or error message.
    """
    client = get_client()
    if not confirm:
        return (
            "Error: Set confirm=True to delete the active note. This is a safety check."
        )

    await client.delete_active_file()
    return "Successfully deleted active note."


@mcp.tool()
@handle_obsidian_errors
@with_client
async def server_status() -> str:
    """Get Obsidian Local REST API server status and authentication info.

    Returns:
        Server status including authentication state and API version.
    """
    client = get_client()
    status = await client.get_server_status()

    if not status:
        return "Unable to get server status."

    output = ["Obsidian Local REST API Status:"]
    for key, value in status.items():
        output.append(f"  {key}: {value}")

    return "\n".join(output)


# NOTE: Disabled due to Obsidian Local REST API routing issues (404 error)
# @mcp.tool()
# @handle_obsidian_errors
# @with_client
# async def get_periodic_note_by_date(
#     period: str,
#     year: int,
#     month: int,
#     day: int,
# ) -> str:
#     """Get a periodic note for a specific date.
#
#     Args:
#         period: Period type - "daily", "weekly", "monthly", "quarterly", or "yearly"
#         year: Year (e.g., 2025)
#         month: Month (1-12)
#         day: Day (1-31)
#
#     Returns:
#         Content of the periodic note for the specified date.
#
#     Note:
#         Requires the Periodic Notes plugin to be installed in Obsidian.
#     """
#     client = get_client()
#     if error := validate_period(period):
#         return error
#
#     result = await client.get_periodic_note_by_date(
#         period, year, month, day, return_metadata=True
#     )
#
#     if isinstance(result, str):
#         return (
#             result
#             if result
#             else f"No {period} note found for {year}-{month:02d}-{day:02d}."
#         )
#
#     # NoteContent object
#     result_parts = []
#     if result.frontmatter:
#         result_parts.append(format_frontmatter(result.frontmatter))
#
#     if result.content:
#         result_parts.append(result.content)
#
#     return (
#         "\n".join(result_parts)
#         if result_parts
#         else f"No {period} note found for {year}-{month:02d}-{day:02d}."
#     )


# ============================================================
# Tier 5: Vector Search Operations
# ============================================================


def _get_vector_store():
    """Get the vector store instance (lazy initialization)."""
    try:
        from .libs.vectorstore.store import ObsidianVectorStore

        config = get_config()
        vector_config = load_vector_config()
        return ObsidianVectorStore(vector_config, config)
    except ImportError:
        raise VectorConfigError(
            "Vector search dependencies not installed. "
            "Install with: pip install 'py-obsidian-tools[vector]'"
        )


@mcp.tool()
async def vector_search(
    query: str,
    n_results: int = 10,
    folder: str | None = None,
) -> str:
    """Perform semantic search across Obsidian vault.

    Args:
        query: Natural language search query
        n_results: Number of results to return (1-100, default: 10)
        folder: Optional folder filter (e.g., "Projects")

    Returns:
        JSON string with search results including path, score, and preview
    """
    try:
        store = _get_vector_store()
        results = await store.async_search(query, n_results, folder)

        return json.dumps(
            {
                "results": [r.model_dump() for r in results],
                "total": len(results),
                "query": query,
            },
            ensure_ascii=False,
            indent=2,
        )

    except IndexNotFoundError as e:
        return json_error("IndexNotFoundError", str(e))
    except VectorConfigError as e:
        return json_error("ConfigurationError", str(e))
    except VectorStoreError as e:
        return json_error("VectorStoreError", str(e))


@mcp.tool()
async def find_similar_notes(
    path: str,
    n_results: int = 5,
) -> str:
    """Find notes similar to a specified note.

    Args:
        path: Path to the source note (e.g., "Projects/MyProject.md")
        n_results: Number of similar notes to return (1-50, default: 5)

    Returns:
        JSON string with similar notes including path, score, and preview
    """
    try:
        store = _get_vector_store()
        results = await store.async_find_similar(path, n_results)

        return json.dumps(
            {
                "source_note": path,
                "similar_notes": [r.model_dump() for r in results],
                "total": len(results),
            },
            ensure_ascii=False,
            indent=2,
        )

    except IndexNotFoundError as e:
        return json_error("IndexNotFoundError", str(e))
    except VectorConfigError as e:
        return json_error("ConfigurationError", str(e))
    except VectorStoreError as e:
        return json_error("VectorStoreError", str(e))


@mcp.tool()
async def vector_status() -> str:
    """Get the status of the vector search index.

    Returns:
        JSON string with index status including document count,
        embedding provider, and last update time
    """
    try:
        store = _get_vector_store()
        status = await store.async_get_status()

        status_dict = status.model_dump()
        # Convert datetime to string for JSON
        if status_dict.get("last_updated"):
            status_dict["last_updated"] = status_dict["last_updated"].isoformat()

        # Add status field
        if status.total_documents > 0:
            status_dict["status"] = "ready"
        else:
            status_dict["status"] = "empty"

        return json.dumps(status_dict, ensure_ascii=False, indent=2)

    except VectorConfigError as e:
        return json_error("ConfigurationError", str(e))
    except VectorStoreError as e:
        return json_error("VectorStoreError", str(e))


# ============================================================
# Entry Point
# ============================================================


def main():
    """Entry point for uvx execution."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
