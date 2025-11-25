# PyObsidianMCP

MCP server for Obsidian via Local REST API - enables AI assistants like Claude to interact with your Obsidian vault.

## Features

- **19 MCP Tools** for complete Obsidian vault management
- **Async HTTP** with httpx for optimal performance
- **UVX Ready** - install and run with a single command
- **Type Safe** - Pydantic models throughout

## Prerequisites

1. **Obsidian** with [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin installed and enabled
2. **API Key** from Obsidian Settings > Local REST API > Security

## Installation

### Using uvx (Recommended)

```bash
uvx pyobsidianmcp
```

### Using pip

```bash
pip install pyobsidianmcp
```

### From source

```bash
git clone https://github.com/rmc8/pyobsidianmcp
cd pyobsidianmcp
uv sync
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required
OBSIDIAN_API_KEY=your-api-key-here

# Optional (defaults shown)
OBSIDIAN_HOST=localhost
OBSIDIAN_PORT=27123
OBSIDIAN_PROTOCOL=http
```

### Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["pyobsidianmcp"],
      "env": {
        "OBSIDIAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Claude Code

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["pyobsidianmcp"],
      "env": {
        "OBSIDIAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### Tier 1: Basic Operations

| Tool | Description |
|------|-------------|
| `list_notes` | List all notes in the vault or a specific directory |
| `read_note` | Read the content of a specific note |
| `search_notes` | Search for notes containing specific text |
| `create_note` | Create a new note with optional frontmatter |

### Tier 2: CRUD Completion

| Tool | Description |
|------|-------------|
| `update_note` | Update (replace) the entire content of a note |
| `append_note` | Append content to the end of a note |
| `delete_note` | Delete a note from the vault (requires `confirm=True`) |

### Tier 3: Advanced Operations

| Tool | Description |
|------|-------------|
| `patch_note` | Update a specific section (heading/block/frontmatter) |
| `list_commands` | List all available Obsidian commands |
| `execute_command` | Execute an Obsidian command |

### Tier 4: Extended Operations

| Tool | Description |
|------|-------------|
| `batch_read_notes` | Read multiple notes at once (comma-separated paths) |
| `complex_search` | Search using JsonLogic queries for advanced filtering |
| `get_recent_changes` | Get recently modified files (requires Dataview plugin) |
| `get_periodic_note` | Get today's daily/weekly/monthly note (requires Periodic Notes plugin) |
| `get_recent_periodic_notes` | Get recent periodic notes |
| `open_note` | Open a note in Obsidian's UI |
| `get_active_note` | Get the currently active note |
| `update_active_note` | Update the active note's content |
| `append_active_note` | Append content to the active note |

## Usage Examples

### List notes in a directory

```
list_notes(directory="daily/2024")
```

### Create a note with frontmatter

```
create_note(
    path="notes/my-note.md",
    content="# My Note\n\nContent here...",
    frontmatter='{"title": "My Note", "tags": ["tag1", "tag2"]}'
)
```

### Search for notes

```
search_notes(query="project ideas")
```

### Patch a specific section

```
patch_note(
    path="notes/my-note.md",
    content="Updated content",
    target_type="heading",
    target="## Section Name",
    operation="replace"
)
```

### Delete a note (with confirmation)

```
delete_note(path="notes/old-note.md", confirm=True)
```

### Read multiple notes at once

```
batch_read_notes(paths="daily/2024-01-01.md,daily/2024-01-02.md,daily/2024-01-03.md")
```

### Complex search with JsonLogic

```
# Find all markdown files in Work folder
complex_search(query='{"glob": ["Work/**/*.md", {"var": "path"}]}')

# Find notes with specific tag
complex_search(query='{"in": ["project", {"var": "tags"}]}')
```

### Get today's daily note

```
get_periodic_note(period="daily")
```

### Get recently modified files

```
get_recent_changes(limit=10, days=7)
```

## Development

```bash
# Install dependencies
uv sync --dev

# Run linter
uv run ruff check src/

# Run with auto-fix
uv run ruff check --fix src/

# Sort imports
uv run isort src/

# Run locally
uv run pyobsidianmcp
```

## License

MIT License - Copyright (c) 2025 rmc8

## Links

- [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
