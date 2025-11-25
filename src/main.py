"""MCP server for Obsidian via Local REST API."""

import json

from mcp.server.fastmcp import FastMCP

from .libs import (ObsidianAPIError, ObsidianClient, ObsidianConfigError,
                   load_config)
from .libs.config import load_vector_config
from .libs.exceptions import (IndexNotFoundError, VectorConfigError,
                              VectorStoreError)

# Initialize FastMCP server
mcp = FastMCP("obsidian")

# Load configuration (lazy validation)
_config = None


def get_config():
    """Get configuration, validating on first access."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


# ============================================================
# Tier 1: Basic Operations
# ============================================================


@mcp.tool()
async def list_notes(directory: str = "") -> str:
    """List all notes in the vault or a specific directory.

    Args:
        directory: Optional subdirectory path (e.g., "daily/2024" or "projects").
                   Leave empty to list all files in the vault root.

    Returns:
        A formatted list of note paths, one per line.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            files = await client.list_files(directory)

            if not files:
                location = f"'{directory}'" if directory else "vault"
                return f"No files found in {location}."

            # Format output
            result = [f"Found {len(files)} file(s):"]
            for f in sorted(files):
                result.append(f"  - {f}")
            return "\n".join(result)

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def read_note(path: str) -> str:
    """Read the content of a specific note.

    Args:
        path: Relative path from vault root (e.g., "daily/2024-01-15.md" or "README.md")

    Returns:
        The note content including frontmatter if present.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            note = await client.get_note(path)

            result_parts = []

            # Add frontmatter if present
            if note.frontmatter:
                fm_lines = ["---"]
                for key, value in note.frontmatter.items():
                    fm_lines.append(f"{key}: {value}")
                fm_lines.append("---")
                result_parts.append("\n".join(fm_lines))

            # Add content
            if note.content:
                result_parts.append(note.content)

            return "\n".join(result_parts) if result_parts else "(empty note)"

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def search_notes(query: str, context_length: int = 100) -> str:
    """Search for notes containing specific text.

    Args:
        query: The search query (text to find)
        context_length: Number of characters of context around matches (default: 100)

    Returns:
        Search results with matching files and context.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
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

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
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
    try:
        config = get_config()
        config.validate_config()

        # Build full content with frontmatter
        full_content_parts = []

        if frontmatter:
            try:
                fm_dict = json.loads(frontmatter)
                if fm_dict:
                    fm_lines = ["---"]
                    for key, value in fm_dict.items():
                        if isinstance(value, list):
                            fm_lines.append(f"{key}:")
                            for item in value:
                                fm_lines.append(f"  - {item}")
                        else:
                            fm_lines.append(f"{key}: {value}")
                    fm_lines.append("---")
                    full_content_parts.append("\n".join(fm_lines))
            except json.JSONDecodeError:
                return "Error: Invalid frontmatter JSON format."

        full_content_parts.append(content)
        full_content = "\n".join(full_content_parts)

        async with ObsidianClient(config) as client:
            await client.create_note(path, full_content)
            return f"Successfully created note: {path}"

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


# ============================================================
# Tier 2: CRUD Completion
# ============================================================


@mcp.tool()
async def update_note(path: str, content: str) -> str:
    """Update (replace) the entire content of an existing note.

    Args:
        path: Path to the note to update
        content: New content (will replace existing content entirely)

    Returns:
        Success or error message.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            await client.update_note(path, content)
            return f"Successfully updated note: {path}"

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def append_note(path: str, content: str) -> str:
    """Append content to the end of an existing note.

    Args:
        path: Path to the note
        content: Content to append

    Returns:
        Success or error message.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            await client.append_note(path, content)
            return f"Successfully appended to note: {path}"

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def delete_note(path: str, confirm: bool = False) -> str:
    """Delete a note from the vault.

    Args:
        path: Path to the note to delete
        confirm: Must be True to actually delete (safety check)

    Returns:
        Success or error message.
    """
    if not confirm:
        return "Error: Set confirm=True to delete the note. This is a safety check."

    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            await client.delete_note(path)
            return f"Successfully deleted note: {path}"

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


# ============================================================
# Tier 3: Advanced Operations
# ============================================================


@mcp.tool()
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
                - For "heading": The heading text (e.g., "## My Section")
                - For "block": The block ID (e.g., "^block-id")
                - For "frontmatter": The field name (e.g., "tags")
        operation: "append", "prepend", or "replace" (default: "replace")

    Returns:
        Success or error message.
    """
    try:
        config = get_config()
        config.validate_config()

        if target_type not in ("heading", "block", "frontmatter"):
            return "Error: target_type must be 'heading', 'block', or 'frontmatter'"

        if operation not in ("append", "prepend", "replace"):
            return "Error: operation must be 'append', 'prepend', or 'replace'"

        async with ObsidianClient(config) as client:
            await client.patch_note(path, content, target_type, target, operation)
            return f"Successfully patched note: {path} ({target_type}: {target})"

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def list_commands() -> str:
    """List all available Obsidian commands.

    Returns:
        A list of available commands with their IDs and names.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            commands = await client.list_commands()

            if not commands:
                return "No commands available."

            output = [f"Available commands ({len(commands)}):"]
            for cmd in sorted(commands, key=lambda c: c.name):
                output.append(f"  - {cmd.name}")
                output.append(f"    ID: {cmd.id}")
            return "\n".join(output)

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def execute_command(command_id: str) -> str:
    """Execute an Obsidian command.

    Args:
        command_id: The command ID to execute (use list_commands to find IDs)

    Returns:
        Success or error message.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            await client.execute_command(command_id)
            return f"Successfully executed command: {command_id}"

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


# ============================================================
# Tier 4: Additional Operations
# ============================================================


@mcp.tool()
async def batch_read_notes(paths: str) -> str:
    """Read multiple notes at once.

    Args:
        paths: Comma-separated list of note paths (e.g., "note1.md,folder/note2.md")

    Returns:
        Contents of all notes with headers.
    """
    try:
        config = get_config()
        config.validate_config()

        path_list = [p.strip() for p in paths.split(",") if p.strip()]
        if not path_list:
            return "Error: No paths provided."

        results = []
        async with ObsidianClient(config) as client:
            for path in path_list:
                try:
                    note = await client.get_note(path)
                    content_parts = [f"# {path}\n"]
                    if note.frontmatter:
                        fm_lines = ["---"]
                        for key, value in note.frontmatter.items():
                            fm_lines.append(f"{key}: {value}")
                        fm_lines.append("---")
                        content_parts.append("\n".join(fm_lines))
                    if note.content:
                        content_parts.append(note.content)
                    results.append("\n".join(content_parts))
                except ObsidianAPIError as e:
                    results.append(f"# {path}\n\nError reading file: {e}")

        return "\n\n---\n\n".join(results)

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
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
    import json as json_module

    try:
        config = get_config()
        config.validate_config()

        try:
            query_dict = json_module.loads(query)
        except json_module.JSONDecodeError:
            return "Error: Invalid JSON query format."

        async with ObsidianClient(config) as client:
            results = await client.search_jsonlogic(query_dict)

            if not results:
                return "No results found."

            output = [f"Found {len(results)} matching file(s):\n"]
            for result in results[:50]:  # Limit to 50 results
                filename = result.get("filename", "Unknown")
                output.append(f"  - {filename}")

            return "\n".join(output)

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
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
    try:
        config = get_config()
        config.validate_config()

        limit = min(max(1, limit), 100)
        days = max(1, days)

        async with ObsidianClient(config) as client:
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

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}. Note: This feature requires the Dataview plugin."


@mcp.tool()
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
    try:
        config = get_config()
        config.validate_config()

        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            return f"Error: Invalid period '{period}'. Must be one of: {', '.join(valid_periods)}"

        async with ObsidianClient(config) as client:
            result = await client.get_periodic_note(period, include_metadata)

            if isinstance(result, str):
                return result if result else f"No {period} note found."

            # NoteContent object
            result_parts = []
            if result.frontmatter:
                fm_lines = ["---"]
                for key, value in result.frontmatter.items():
                    fm_lines.append(f"{key}: {value}")
                fm_lines.append("---")
                result_parts.append("\n".join(fm_lines))

            if result.content:
                result_parts.append(result.content)

            return (
                "\n".join(result_parts) if result_parts else f"No {period} note found."
            )

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}. Note: This feature requires the Periodic Notes plugin."


@mcp.tool()
async def get_recent_periodic_notes(
    period: str,
    limit: int = 5,
    include_content: bool = False,
) -> str:
    """Get recent periodic notes for the specified period type.

    Args:
        period: Period type - "daily", "weekly", "monthly", "quarterly", or "yearly"
        limit: Maximum number of notes to return (1-50, default: 5)
        include_content: Whether to include note content (default: False)

    Returns:
        List of recent periodic notes.

    Note:
        Requires the Periodic Notes plugin to be installed in Obsidian.
    """
    try:
        config = get_config()
        config.validate_config()

        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            return f"Error: Invalid period '{period}'. Must be one of: {', '.join(valid_periods)}"

        limit = min(max(1, limit), 50)

        async with ObsidianClient(config) as client:
            results = await client.get_recent_periodic_notes(
                period, limit, include_content
            )

            if not results:
                return f"No recent {period} notes found."

            output = [f"Recent {period} notes ({len(results)}):\n"]
            for note in results:
                if isinstance(note, dict):
                    path = note.get("path", note.get("filename", "Unknown"))
                    output.append(f"  - {path}")
                    if include_content and "content" in note:
                        output.append(
                            f"    Content preview: {note['content'][:100]}..."
                        )
                else:
                    output.append(f"  - {note}")

            return "\n".join(output)

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}. Note: This feature requires the Periodic Notes plugin."


@mcp.tool()
async def open_note(path: str, new_leaf: bool = False) -> str:
    """Open a note in Obsidian's UI.

    Args:
        path: Path to the note to open
        new_leaf: Whether to open in a new tab (default: False)

    Returns:
        Success or error message.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            await client.open_file(path, new_leaf)
            return f"Successfully opened note: {path}"

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def get_active_note() -> str:
    """Get the currently active note in Obsidian.

    Returns:
        Content of the active note, or error if no note is active.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            note = await client.get_active_file()

            if note is None:
                return "No active note in Obsidian."

            result_parts = []
            if note.path:
                result_parts.append(f"Path: {note.path}\n")

            if note.frontmatter:
                fm_lines = ["---"]
                for key, value in note.frontmatter.items():
                    fm_lines.append(f"{key}: {value}")
                fm_lines.append("---")
                result_parts.append("\n".join(fm_lines))

            if note.content:
                result_parts.append(note.content)

            return "\n".join(result_parts) if result_parts else "(empty note)"

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def update_active_note(content: str) -> str:
    """Update (replace) the content of the currently active note.

    Args:
        content: New content for the note (will replace existing content)

    Returns:
        Success or error message.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            await client.update_active_file(content)
            return "Successfully updated active note."

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def append_active_note(content: str) -> str:
    """Append content to the currently active note.

    Args:
        content: Content to append to the note

    Returns:
        Success or error message.
    """
    try:
        config = get_config()
        config.validate_config()

        async with ObsidianClient(config) as client:
            await client.append_active_file(content)
            return "Successfully appended to active note."

    except ObsidianConfigError as e:
        return f"Configuration Error: {e}"
    except ObsidianAPIError as e:
        return f"Error: {e}"


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
            "Install with: pip install 'pyobsidianmcp[vector]'"
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
        return json.dumps(
            {
                "error": True,
                "error_type": "IndexNotFoundError",
                "message": str(e),
            },
            ensure_ascii=False,
        )
    except VectorConfigError as e:
        return json.dumps(
            {
                "error": True,
                "error_type": "ConfigurationError",
                "message": str(e),
            },
            ensure_ascii=False,
        )
    except VectorStoreError as e:
        return json.dumps(
            {
                "error": True,
                "error_type": "VectorStoreError",
                "message": str(e),
            },
            ensure_ascii=False,
        )


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
        return json.dumps(
            {
                "error": True,
                "error_type": "IndexNotFoundError",
                "message": str(e),
            },
            ensure_ascii=False,
        )
    except VectorConfigError as e:
        return json.dumps(
            {
                "error": True,
                "error_type": "ConfigurationError",
                "message": str(e),
            },
            ensure_ascii=False,
        )
    except VectorStoreError as e:
        return json.dumps(
            {
                "error": True,
                "error_type": "VectorStoreError",
                "message": str(e),
            },
            ensure_ascii=False,
        )


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
        return json.dumps(
            {
                "error": True,
                "error_type": "ConfigurationError",
                "message": str(e),
            },
            ensure_ascii=False,
        )
    except VectorStoreError as e:
        return json.dumps(
            {
                "error": True,
                "error_type": "VectorStoreError",
                "message": str(e),
            },
            ensure_ascii=False,
        )


# ============================================================
# Entry Point
# ============================================================


def main():
    """Entry point for uvx execution."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
