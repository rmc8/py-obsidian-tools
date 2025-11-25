"""Obsidian Local REST API client using httpx."""

from typing import Any
from urllib.parse import quote

import httpx

from .config import ObsidianConfig
from .exceptions import (ObsidianAPIError, ObsidianAuthError,
                         ObsidianConnectionError, ObsidianNotFoundError)
from .models import CommandInfo, NoteContent, SearchMatch, SearchResult


class ObsidianClient:
    """Async client for Obsidian Local REST API."""

    def __init__(self, config: ObsidianConfig):
        """Initialize the client with configuration."""
        self.config = config
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "ObsidianClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Make an HTTP request with error handling."""
        if not self._client:
            raise ObsidianAPIError("Client not initialized. Use 'async with' context.")

        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            response = await self._client.request(
                method, endpoint, headers=request_headers, **kwargs
            )
            response.raise_for_status()

            if response.status_code == 204 or not response.content:
                return None

            content_type = response.headers.get("content-type", "")
            if (
                "application/json" in content_type
                or "application/vnd.olrapi" in content_type
            ):
                return response.json()
            return response.text

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 404:
                raise ObsidianNotFoundError(f"Not found: {endpoint}") from e
            if status_code in (401, 403):
                raise ObsidianAuthError(
                    "Authentication failed. Check your OBSIDIAN_API_KEY."
                ) from e
            raise ObsidianAPIError(
                f"HTTP {status_code}: {e.response.text[:200]}"
            ) from e

        except httpx.ConnectError as e:
            raise ObsidianConnectionError(
                f"Cannot connect to {self.config.base_url}. "
                "Ensure Obsidian is running with Local REST API plugin enabled."
            ) from e

        except httpx.RequestError as e:
            raise ObsidianAPIError(f"Request error: {e}") from e

    # ========== Vault Operations ==========

    async def list_files(self, directory: str = "") -> list[str]:
        """List files in the vault or a specific directory."""
        endpoint = f"/vault/{directory}" if directory else "/vault/"
        if directory and not endpoint.endswith("/"):
            endpoint += "/"

        response = await self._request("GET", endpoint)
        if isinstance(response, dict) and "files" in response:
            return response["files"]
        return []

    async def get_note(self, path: str) -> NoteContent:
        """Get note content with frontmatter and metadata."""
        encoded_path = quote(path, safe="/")
        response = await self._request(
            "GET",
            f"/vault/{encoded_path}",
            headers={"Accept": "application/vnd.olrapi.note+json"},
        )

        if isinstance(response, dict):
            return NoteContent(**response)
        # Plain text response
        return NoteContent(content=response or "")

    async def get_note_raw(self, path: str) -> str:
        """Get raw note content as markdown."""
        encoded_path = quote(path, safe="/")
        response = await self._request(
            "GET",
            f"/vault/{encoded_path}",
            headers={"Accept": "text/markdown"},
        )
        return response or ""

    async def create_note(self, path: str, content: str) -> None:
        """Create or replace a note (PUT)."""
        encoded_path = quote(path, safe="/")
        await self._request(
            "PUT",
            f"/vault/{encoded_path}",
            content=content,
            headers={"Content-Type": "text/markdown"},
        )

    async def update_note(self, path: str, content: str) -> None:
        """Update (replace) a note's content."""
        await self.create_note(path, content)

    async def append_note(self, path: str, content: str) -> None:
        """Append content to an existing note (POST)."""
        encoded_path = quote(path, safe="/")
        await self._request(
            "POST",
            f"/vault/{encoded_path}",
            content=content,
            headers={"Content-Type": "text/markdown"},
        )

    async def patch_note(
        self,
        path: str,
        content: str,
        target_type: str,
        target: str,
        operation: str = "replace",
    ) -> None:
        """Patch a specific section of a note.

        Args:
            path: Note path
            content: New content
            target_type: "heading", "block", or "frontmatter"
            target: Target identifier (heading text, block ID, or frontmatter field)
            operation: "append", "prepend", or "replace"
        """
        encoded_path = quote(path, safe="/")
        encoded_target = quote(target)  # URL encode for non-ASCII characters
        await self._request(
            "PATCH",
            f"/vault/{encoded_path}",
            content=content,
            headers={
                "Content-Type": "text/markdown",
                "Operation": operation,
                "Target-Type": target_type,
                "Target": encoded_target,
            },
        )

    async def delete_note(self, path: str) -> None:
        """Delete a note."""
        encoded_path = quote(path, safe="/")
        await self._request("DELETE", f"/vault/{encoded_path}")

    # ========== Search Operations ==========

    async def search_simple(
        self, query: str, context_length: int = 100
    ) -> list[SearchResult]:
        """Perform a simple text search across the vault."""
        response = await self._request(
            "POST",
            "/search/simple/",
            json={"query": query, "contextLength": context_length},
        )

        results = []
        if isinstance(response, list):
            for item in response:
                if isinstance(item, dict):
                    matches = []
                    for m in item.get("matches", []):
                        if isinstance(m, dict):
                            matches.append(
                                SearchMatch(
                                    match=m.get("match", ""),
                                    context=m.get("context", ""),
                                )
                            )
                    results.append(
                        SearchResult(
                            filename=item.get("filename", ""),
                            matches=matches,
                            score=item.get("score"),
                        )
                    )
        return results

    # ========== Command Operations ==========

    async def list_commands(self) -> list[CommandInfo]:
        """List all available Obsidian commands."""
        response = await self._request("GET", "/commands/")

        commands = []
        if isinstance(response, dict) and "commands" in response:
            for cmd in response["commands"]:
                if isinstance(cmd, dict):
                    commands.append(
                        CommandInfo(
                            id=cmd.get("id", ""),
                            name=cmd.get("name", ""),
                        )
                    )
        return commands

    async def execute_command(self, command_id: str) -> None:
        """Execute an Obsidian command by ID."""
        encoded_id = quote(command_id, safe="")
        await self._request("POST", f"/commands/{encoded_id}/")

    # ========== Active File Operations ==========

    async def get_active_file(self) -> NoteContent | None:
        """Get the currently active file in Obsidian."""
        try:
            response = await self._request(
                "GET",
                "/active/",
                headers={"Accept": "application/vnd.olrapi.note+json"},
            )
            if isinstance(response, dict):
                return NoteContent(**response)
            return NoteContent(content=response or "")
        except ObsidianNotFoundError:
            return None

    async def update_active_file(self, content: str) -> None:
        """Update (replace) the content of the active file."""
        await self._request(
            "PUT",
            "/active/",
            content=content,
            headers={"Content-Type": "text/markdown"},
        )

    async def append_active_file(self, content: str) -> None:
        """Append content to the active file."""
        await self._request(
            "POST",
            "/active/",
            content=content,
            headers={"Content-Type": "text/markdown"},
        )

    # ========== Complex Search Operations ==========

    async def search_jsonlogic(self, query: dict) -> list[dict]:
        """Perform a JsonLogic search across the vault.

        Args:
            query: JsonLogic query object
                   Example: {"glob": ["*.md", {"var": "path"}]}
                   Example: {"and": [
                       {"glob": ["*.md", {"var": "path"}]},
                       {"regexp": [".*Work.*", {"var": "path"}]}
                   ]}

        Returns:
            List of matching results with filename and result fields.
        """
        response = await self._request(
            "POST",
            "/search/",
            json=query,
            headers={"Content-Type": "application/vnd.olrapi.jsonlogic+json"},
        )
        return response if isinstance(response, list) else []

    async def search_dataview(self, dql: str) -> list[dict]:
        """Perform a Dataview DQL search.

        Args:
            dql: Dataview Query Language string
                 Example: "TABLE file.mtime WHERE file.mtime >= date(today) - dur(7 days)"

        Returns:
            List of matching results.

        Note:
            Requires the Dataview plugin to be installed in Obsidian.
        """
        response = await self._request(
            "POST",
            "/search/",
            content=dql.encode("utf-8"),
            headers={"Content-Type": "application/vnd.olrapi.dataview.dql+txt"},
        )
        return response if isinstance(response, list) else []

    # ========== Periodic Notes Operations ==========

    async def get_periodic_note(
        self,
        period: str,
        return_metadata: bool = False,
    ) -> NoteContent | str:
        """Get the current periodic note for the specified period.

        Args:
            period: Period type - "daily", "weekly", "monthly", "quarterly", or "yearly"
            return_metadata: If True, return NoteContent with metadata; else raw content

        Returns:
            NoteContent with metadata if return_metadata=True, else raw markdown string.

        Note:
            Requires the Periodic Notes plugin to be installed in Obsidian.
        """
        headers = {}
        if return_metadata:
            headers["Accept"] = "application/vnd.olrapi.note+json"

        response = await self._request("GET", f"/periodic/{period}/", headers=headers)

        if return_metadata and isinstance(response, dict):
            return NoteContent(**response)
        return response or ""

    async def get_recent_periodic_notes(
        self,
        period: str,
        limit: int = 5,
        include_content: bool = False,
    ) -> list[dict]:
        """Get recent periodic notes for the specified period type.

        Args:
            period: Period type - "daily", "weekly", "monthly", "quarterly", or "yearly"
            limit: Maximum number of notes to return (1-50, default: 5)
            include_content: Whether to include note content

        Returns:
            List of periodic note information.

        Note:
            Requires the Periodic Notes plugin to be installed in Obsidian.
        """
        response = await self._request(
            "GET",
            f"/periodic/{period}/recent",
            params={"limit": limit, "includeContent": str(include_content).lower()},
        )
        return response if isinstance(response, list) else []

    async def append_periodic_note(self, period: str, content: str) -> None:
        """Append content to the current periodic note.

        Args:
            period: Period type - "daily", "weekly", "monthly", "quarterly", or "yearly"
            content: Content to append
        """
        await self._request(
            "POST",
            f"/periodic/{period}/",
            content=content,
            headers={"Content-Type": "text/markdown"},
        )

    # ========== Recent Changes ==========

    async def get_recent_changes(self, limit: int = 10, days: int = 90) -> list[dict]:
        """Get recently modified files in the vault.

        Args:
            limit: Maximum number of files to return (default: 10)
            days: Only include files modified within this many days (default: 90)

        Returns:
            List of recently modified files with metadata.

        Note:
            Requires the Dataview plugin to be installed in Obsidian.
        """
        dql = f"""TABLE file.mtime
WHERE file.mtime >= date(today) - dur({days} days)
SORT file.mtime DESC
LIMIT {limit}"""

        return await self.search_dataview(dql)

    # ========== Open File ==========

    async def open_file(self, path: str, new_leaf: bool = False) -> None:
        """Open a file in Obsidian's UI.

        Args:
            path: Path to the file to open
            new_leaf: Whether to open in a new tab/leaf
        """
        encoded_path = quote(path, safe="/")
        params = {"newLeaf": "true"} if new_leaf else {}
        await self._request("POST", f"/open/{encoded_path}", params=params)
