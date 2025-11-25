"""Custom exception hierarchy for Obsidian API errors."""


class ObsidianAPIError(Exception):
    """Base exception for Obsidian API errors."""

    pass


class ObsidianNotFoundError(ObsidianAPIError):
    """Resource not found (HTTP 404)."""

    pass


class ObsidianAuthError(ObsidianAPIError):
    """Authentication failed (HTTP 401/403)."""

    pass


class ObsidianConnectionError(ObsidianAPIError):
    """Network connection issues."""

    pass


class ObsidianConfigError(ObsidianAPIError):
    """Configuration errors (missing or invalid settings)."""

    pass
