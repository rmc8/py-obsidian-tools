🌐 **Language / 言語**: [English](README.md) | [简体中文](docs/README/README_ZH.md) | [繁體中文](docs/README/README_TW.md) | [Español](docs/README/README_ES.md) | [Français](docs/README/README_FR.md) | [Português](docs/README/README_PT.md) | [Deutsch](docs/README/README_DE.md) | [Русский](docs/README/README_RU.md) | [日本語](docs/README/README_JA.md) | [한국어](docs/README/README_KO.md) | [हिन्दी](docs/README/README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/commits)

# py-obsidian-tools

MCP server to interact with Obsidian via the Local REST API community plugin.

## Components

### Tools

The server implements multiple tools to interact with Obsidian:

| Tool | Description |
|------|-------------|
| `list_notes` | List all notes in the vault or a specific directory |
| `read_note` | Read the content of a specific note |
| `search_notes` | Search for notes containing specific text |
| `create_note` | Create a new note with optional frontmatter |
| `update_note` | Update (replace) the entire content of a note |
| `append_note` | Append content to the end of a note |
| `delete_note` | Delete a note from the vault |
| `patch_note` | Update a specific section (heading/block/frontmatter) |
| `list_commands` | List all available Obsidian commands |
| `execute_command` | Execute an Obsidian command |
| `batch_read_notes` | Read multiple notes at once |
| `complex_search` | Search using JsonLogic queries for advanced filtering |
| `get_recent_changes` | Get recently modified files (requires Dataview plugin) |
| `get_periodic_note` | Get today's daily/weekly/monthly note (requires Periodic Notes plugin) |
| `open_note` | Open a note in Obsidian's UI |
| `get_active_note` | Get the currently active note |
| `update_active_note` | Update the active note's content |
| `append_active_note` | Append content to the active note |
| `patch_active_note` | Update a specific section of the active note |
| `delete_active_note` | Delete the currently active note |
| `server_status` | Get Obsidian Local REST API server status |
| `dataview_query` | Execute Dataview DQL queries (requires Dataview plugin) |
| `vector_search` | Semantic search across notes using natural language (requires vector extras) |
| `find_similar_notes` | Find notes similar to a specified note (requires vector extras) |
| `vector_status` | Get status of the vector search index (requires vector extras) |

### Example prompts

It is good to first instruct Claude to use Obsidian. Then it will always call the tool.

You can use prompts like this:
- "List all notes in the 'Daily' folder"
- "Search for all notes mentioning 'Project X' and summarize them"
- "Create a new note called 'Meeting Notes' with the content of our discussion"
- "Append 'TODO: Review PR' to my daily note"
- "Get the content of the active note and critique it"
- "Find all markdown files in the Work folder using complex search"
- "Search for notes about machine learning using semantic search"
- "Find notes similar to my project plan"
- "Run a Dataview query to list all notes with the tag #project"
- "Get today's daily note"
- "Update the 'Tasks' section of the active note"
- "Check the Obsidian API server status"

## Configuration

### Obsidian REST API Key

There are two ways to configure the environment with the Obsidian REST API Key.

1. Add to server config (preferred)

```json
{
  "mcpServers": {
    "obsidian-tools": {
      "command": "uvx",
      "args": ["py-obsidian-tools"],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
}
```

2. Create a `.env` file in the working directory with the following required variables:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27124
```

Note:
- You can find the API key in the Obsidian plugin config (Settings > Local REST API > Security)
- Default port is 27124
- Default host is 127.0.0.1 (localhost)

## Quickstart

### Install

#### Obsidian REST API

You need the Obsidian REST API community plugin running: https://github.com/coddingtonbear/obsidian-local-rest-api

Install and enable it in the settings and copy the API key.

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

**Recommended: Install from PyPI (uvx)**

```json
{
  "mcpServers": {
    "obsidian-tools": {
      "command": "uvx",
      "args": ["py-obsidian-tools"],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
}
```

<details>
  <summary>Development/Unpublished Servers Configuration</summary>

```json
{
  "mcpServers": {
    "obsidian-tools": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/py-obsidian-tools",
        "run",
        "py-obsidian-tools"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>"
      }
    }
  }
}
```
</details>

<details>
  <summary>Install from GitHub (uvx)</summary>

```json
{
  "mcpServers": {
    "obsidian-tools": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/rmc8/py-obsidian-tools",
        "py-obsidian-tools"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>"
      }
    }
  }
}
```
</details>

## Vector Search (Optional)

Semantic search functionality using ChromaDB. This feature allows natural language queries across your vault.

### Installation

**Using uvx (recommended)**:

```bash
# No installation required - run directly with uvx
uvx --from 'py-obsidian-tools[vector]' pyobsidian-index full --verbose
```

**Using pip**:

```bash
# Basic (local embeddings - no API key required)
pip install "py-obsidian-tools[vector]"

# With external embedding providers
pip install "py-obsidian-tools[vector-openai]"
pip install "py-obsidian-tools[vector-google]"
pip install "py-obsidian-tools[vector-cohere]"
pip install "py-obsidian-tools[vector-all]"
```

### Create Index

Before using vector search, you need to create an index of your vault:

```bash
# Using uvx (recommended - no installation required)
uvx --from 'py-obsidian-tools[vector]' pyobsidian-index full --verbose

# Or if installed via pip
pyobsidian-index full --verbose
```

> **Note**: The `pyobsidian-index` command requires the `[vector]` extras. When using uvx, you must include `[vector]` in the package specification. Running `uvx --from py-obsidian-tools pyobsidian-index` without `[vector]` will fail.

### CLI Commands

```bash
# Using uvx
uvx --from 'py-obsidian-tools[vector]' pyobsidian-index <command>

# Using pip installation
pyobsidian-index <command>
```

| Command | Description |
|---------|-------------|
| `full` | Index all notes in the vault |
| `update` | Incremental update (new/modified notes only) |
| `clear` | Clear the entire index |
| `status` | Show index status |

### Environment Variables

```bash
VECTOR_PROVIDER=default          # default, ollama, openai, google, cohere
VECTOR_CHROMA_PATH=~/.obsidian-vector
VECTOR_CHUNK_SIZE=512

# For Ollama
VECTOR_OLLAMA_HOST=http://localhost:11434
VECTOR_OLLAMA_MODEL=nomic-embed-text

# For OpenAI
VECTOR_OPENAI_API_KEY=sk-xxx
VECTOR_OPENAI_MODEL=text-embedding-3-small

# For Google
VECTOR_GOOGLE_API_KEY=xxx
VECTOR_GOOGLE_MODEL=embedding-001

# For Cohere
VECTOR_COHERE_API_KEY=xxx
VECTOR_COHERE_MODEL=embed-multilingual-v3.0
```

### Embedding Providers

| Provider | Model | Best For |
|----------|-------|----------|
| default | all-MiniLM-L6-v2 | Fast, free, completely local |
| ollama | nomic-embed-text | High quality, local |
| openai | text-embedding-3-small | Best quality, multilingual |
| google | embedding-001 | Google AI integration |
| cohere | embed-multilingual-v3.0 | Multilingual specialization |

## Development

### Building

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via `npx` with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/py-obsidian-tools run py-obsidian-tools
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

You can also watch the server logs (if configured) or use standard python logging.
