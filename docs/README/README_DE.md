🌐 **Language / 言語**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/commits)

# PyObsidianMCP

MCP-Server zur Interaktion mit Obsidian über das Local REST API Community-Plugin.

## Komponenten

### Werkzeuge

Der Server implementiert mehrere Werkzeuge zur Interaktion mit Obsidian:

| Werkzeug | Beschreibung |
|----------|--------------|
| `list_notes` | Listet alle Notizen im Vault oder einem bestimmten Verzeichnis auf |
| `read_note` | Liest den Inhalt einer bestimmten Notiz |
| `search_notes` | Sucht nach Notizen, die bestimmten Text enthalten |
| `create_note` | Erstellt eine neue Notiz mit optionalem Frontmatter |
| `update_note` | Aktualisiert (ersetzt) den gesamten Inhalt einer Notiz |
| `append_note` | Fügt Inhalt am Ende einer Notiz hinzu |
| `delete_note` | Löscht eine Notiz aus dem Vault |
| `patch_note` | Aktualisiert einen bestimmten Abschnitt (Überschrift/Block/Frontmatter) |
| `list_commands` | Listet alle verfügbaren Obsidian-Befehle auf |
| `execute_command` | Führt einen Obsidian-Befehl aus |
| `batch_read_notes` | Liest mehrere Notizen auf einmal |
| `complex_search` | Suche mit JsonLogic-Abfragen für erweiterte Filterung |
| `get_recent_changes` | Ruft kürzlich geänderte Dateien ab (erfordert Dataview-Plugin) |
| `get_periodic_note` | Ruft die heutige tägliche/wöchentliche/monatliche Notiz ab (erfordert Periodic Notes-Plugin) |
| `get_periodic_note_by_date` | Ruft die periodische Notiz eines bestimmten Datums ab (erfordert Periodic Notes-Plugin) |
| `get_recent_periodic_notes` | Ruft aktuelle periodische Notizen ab (erfordert Dataview-Plugin) |
| `open_note` | Öffnet eine Notiz in der Obsidian-Oberfläche |
| `get_active_note` | Ruft die aktuell aktive Notiz ab |
| `update_active_note` | Aktualisiert den Inhalt der aktiven Notiz |
| `append_active_note` | Fügt Inhalt zur aktiven Notiz hinzu |
| `patch_active_note` | Aktualisiert einen bestimmten Abschnitt der aktiven Notiz |
| `delete_active_note` | Löscht die aktuell aktive Notiz |
| `server_status` | Ruft den Status des Obsidian Local REST API-Servers ab |
| `dataview_query` | Führt Dataview DQL-Abfragen aus (erfordert Dataview-Plugin) |
| `vector_search` | Semantische Suche mit natürlicher Sprache (erfordert vector extras) |
| `find_similar_notes` | Findet ähnliche Notizen zu einer bestimmten Notiz (erfordert vector extras) |
| `vector_status` | Ruft den Status des Vektor-Suchindex ab (erfordert vector extras) |

### Beispiel-Prompts

Es ist gut, Claude zuerst anzuweisen, Obsidian zu verwenden. Dann wird es immer das Werkzeug aufrufen.

Sie können Prompts wie diese verwenden:
- "Liste alle Notizen im Ordner 'Daily' auf"
- "Suche alle Notizen, die 'Projekt X' erwähnen, und fasse sie zusammen"
- "Erstelle eine neue Notiz namens 'Besprechungsnotizen' mit dem Inhalt unserer Diskussion"
- "Füge 'TODO: PR überprüfen' zu meiner täglichen Notiz hinzu"
- "Hole den Inhalt der aktiven Notiz und kritisiere ihn"
- "Finde alle Markdown-Dateien im Work-Ordner mit complex search"
- "Suche Notizen über maschinelles Lernen mit semantischer Suche"
- "Finde ähnliche Notizen zu meinem Projektplan"

## Konfiguration

### Obsidian REST API-Schlüssel

Es gibt zwei Möglichkeiten, die Umgebung mit dem Obsidian REST API-Schlüssel zu konfigurieren.

1. Zur Server-Konfiguration hinzufügen (empfohlen)

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

2. Erstellen Sie eine `.env`-Datei im Arbeitsverzeichnis mit den folgenden erforderlichen Variablen:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27124
```

Hinweis:
- Den API-Schlüssel finden Sie in der Obsidian-Plugin-Konfiguration (Einstellungen > Local REST API > Sicherheit)
- Standard-Port ist 27124
- Standard-Host ist 127.0.0.1 (localhost)

## Schnellstart

### Installation

#### Obsidian REST API

Sie benötigen das laufende Obsidian REST API Community-Plugin: https://github.com/coddingtonbear/obsidian-local-rest-api

Installieren und aktivieren Sie es in den Einstellungen und kopieren Sie den API-Schlüssel.

#### Claude Desktop

Auf MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

Auf Windows: `%APPDATA%/Claude/claude_desktop_config.json`

**Empfohlen: Von PyPI installieren (uvx)**

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
  <summary>Entwicklungs-/Unveröffentlichte Server-Konfiguration</summary>

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
  <summary>Von GitHub installieren (uvx)</summary>

```json
{
  "mcpServers": {
    "obsidian-tools": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/rmc8/PyObsidianMCP",
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

## Vektorsuche (Optional)

Semantische Suchfunktionalität mit ChromaDB. Diese Funktion ermöglicht natürlichsprachliche Abfragen über Ihren gesamten Vault.

### Installation

```bash
# Basis (lokale Embeddings - kein API-Schlüssel erforderlich)
pip install "py-obsidian-tools[vector]"

# Mit externen Embedding-Anbietern
pip install "py-obsidian-tools[vector-openai]"
pip install "py-obsidian-tools[vector-google]"
pip install "py-obsidian-tools[vector-cohere]"
pip install "py-obsidian-tools[vector-all]"
```

### Index erstellen

Bevor Sie die Vektorsuche verwenden, müssen Sie einen Index Ihres Vaults erstellen:

```bash
# Methode 1: Falls bereits installiert
pyobsidian-index full --verbose

# Methode 2: Mit uvx (keine Installation erforderlich)
uvx --from py-obsidian-tools pyobsidian-index full --verbose
```

### CLI-Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `pyobsidian-index full` | Alle Notizen im Vault indizieren |
| `pyobsidian-index update` | Inkrementelles Update (nur neue/geänderte Notizen) |
| `pyobsidian-index clear` | Gesamten Index löschen |
| `pyobsidian-index status` | Index-Status anzeigen |

### Umgebungsvariablen

```bash
VECTOR_PROVIDER=default          # default, ollama, openai, google, cohere
VECTOR_CHROMA_PATH=~/.obsidian-vector
VECTOR_CHUNK_SIZE=512

# Für Ollama
VECTOR_OLLAMA_HOST=http://localhost:11434
VECTOR_OLLAMA_MODEL=nomic-embed-text

# Für OpenAI
VECTOR_OPENAI_API_KEY=sk-xxx
VECTOR_OPENAI_MODEL=text-embedding-3-small

# Für Google
VECTOR_GOOGLE_API_KEY=xxx
VECTOR_GOOGLE_MODEL=embedding-001

# Für Cohere
VECTOR_COHERE_API_KEY=xxx
VECTOR_COHERE_MODEL=embed-multilingual-v3.0
```

### Embedding-Anbieter

| Anbieter | Modell | Optimal Für |
|----------|--------|-------------|
| default | all-MiniLM-L6-v2 | Schnell, kostenlos, vollständig lokal |
| ollama | nomic-embed-text | Hohe Qualität, lokal |
| openai | text-embedding-3-small | Beste Qualität, mehrsprachig |
| google | embedding-001 | Google AI Integration |
| cohere | embed-multilingual-v3.0 | Mehrsprachig-Spezialisierung |

## Entwicklung

### Bauen

Um das Paket für die Verteilung vorzubereiten:

1. Abhängigkeiten synchronisieren und Lockfile aktualisieren:
```bash
uv sync
```

### Debugging

Da MCP-Server über stdio laufen, kann das Debugging eine Herausforderung sein. Für die beste Debugging-Erfahrung empfehlen wir dringend die Verwendung des [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

Sie können den MCP Inspector über `npx` mit diesem Befehl starten:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/py-obsidian-tools run py-obsidian-tools
```

Nach dem Start zeigt der Inspector eine URL an, die Sie in Ihrem Browser aufrufen können, um mit dem Debugging zu beginnen.

Sie können auch die Server-Logs beobachten (falls konfiguriert) oder Standard-Python-Logging verwenden.
