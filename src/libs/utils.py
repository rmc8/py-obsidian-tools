"""Utility functions for py-obsidian-tools."""

import json
from typing import Any

# Valid periods for periodic notes
VALID_PERIODS = ("daily", "weekly", "monthly", "quarterly", "yearly")

# Valid target types for patch operations
VALID_TARGET_TYPES = ("heading", "block", "frontmatter")

# Valid operations for patch
VALID_OPERATIONS = ("append", "prepend", "replace")


def format_frontmatter(frontmatter: dict[str, Any] | None) -> str:
    """Convert frontmatter dict to YAML-formatted string.

    Args:
        frontmatter: Dictionary containing frontmatter key-value pairs.

    Returns:
        YAML-formatted string with --- delimiters, or empty string if None/empty.
    """
    if not frontmatter:
        return ""

    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def validate_period(period: str) -> str | None:
    """Validate period type for periodic notes.

    Args:
        period: Period type to validate.

    Returns:
        Error message if invalid, None if valid.
    """
    if period not in VALID_PERIODS:
        return f"Error: Invalid period '{period}'. Must be one of: {', '.join(VALID_PERIODS)}"
    return None


def validate_patch_params(target_type: str, operation: str) -> str | None:
    """Validate parameters for patch operations.

    Args:
        target_type: Type of target (heading, block, frontmatter).
        operation: Operation type (append, prepend, replace).

    Returns:
        Error message if invalid, None if valid.
    """
    if target_type not in VALID_TARGET_TYPES:
        return f"Error: target_type must be one of: {', '.join(VALID_TARGET_TYPES)}"
    if operation not in VALID_OPERATIONS:
        return f"Error: operation must be one of: {', '.join(VALID_OPERATIONS)}"
    return None


def json_error(error_type: str, message: str) -> str:
    """Create standardized JSON error response.

    Args:
        error_type: Type/category of the error.
        message: Human-readable error message.

    Returns:
        JSON string with error structure.
    """
    return json.dumps(
        {
            "error": True,
            "error_type": error_type,
            "message": message,
        },
        ensure_ascii=False,
    )


def format_note_content(
    content: str | None,
    frontmatter: dict[str, Any] | None = None,
    path: str | None = None,
) -> str:
    """Format note content with optional frontmatter and path header.

    Args:
        content: Note content.
        frontmatter: Optional frontmatter dictionary.
        path: Optional path to include as header.

    Returns:
        Formatted note content string.
    """
    parts = []

    if path:
        parts.append(f"Path: {path}\n")

    if frontmatter:
        parts.append(format_frontmatter(frontmatter))

    if content:
        parts.append(content)

    return "\n".join(parts) if parts else "(empty note)"
