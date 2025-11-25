🌐 **Language / 言語**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/commits)

# PyObsidianMCP

Servidor MCP para interactuar con Obsidian a través del plugin comunitario Local REST API.

## Componentes

### Herramientas

El servidor implementa múltiples herramientas para interactuar con Obsidian:

| Herramienta | Descripción |
|-------------|-------------|
| `list_notes` | Lista todas las notas en el vault o en un directorio específico |
| `read_note` | Lee el contenido de una nota específica |
| `search_notes` | Busca notas que contengan texto específico |
| `create_note` | Crea una nueva nota con frontmatter opcional |
| `update_note` | Actualiza (reemplaza) el contenido completo de una nota |
| `append_note` | Añade contenido al final de una nota |
| `delete_note` | Elimina una nota del vault |
| `patch_note` | Actualiza una sección específica (encabezado/bloque/frontmatter) |
| `list_commands` | Lista todos los comandos de Obsidian disponibles |
| `execute_command` | Ejecuta un comando de Obsidian |
| `batch_read_notes` | Lee múltiples notas a la vez |
| `complex_search` | Búsqueda con consultas JsonLogic para filtrado avanzado |
| `get_recent_changes` | Obtiene archivos modificados recientemente (requiere plugin Dataview) |
| `get_periodic_note` | Obtiene la nota diaria/semanal/mensual de hoy (requiere plugin Periodic Notes) |
| `get_recent_periodic_notes` | Obtiene notas periódicas recientes |
| `open_note` | Abre una nota en la interfaz de Obsidian |
| `get_active_note` | Obtiene la nota actualmente activa |
| `update_active_note` | Actualiza el contenido de la nota activa |
| `append_active_note` | Añade contenido a la nota activa |

### Ejemplos de prompts

Es bueno primero indicarle a Claude que use Obsidian. Entonces siempre llamará a la herramienta.

Puedes usar prompts como estos:
- "Lista todas las notas en la carpeta 'Daily'"
- "Busca todas las notas que mencionen 'Proyecto X' y resúmelas"
- "Crea una nueva nota llamada 'Notas de Reunión' con el contenido de nuestra discusión"
- "Añade 'TODO: Revisar PR' a mi nota diaria"
- "Obtén el contenido de la nota activa y critícalo"
- "Encuentra todos los archivos markdown en la carpeta Work usando complex search"

## Configuración

### Clave API de Obsidian REST

Hay dos formas de configurar el entorno con la clave API de Obsidian REST.

1. Añadir a la configuración del servidor (recomendado)

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/rmc8/PyObsidianMCP",
        "pyobsidianmcp"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27123"
      }
    }
  }
}
```

2. Crear un archivo `.env` en el directorio de trabajo con las siguientes variables requeridas:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123
```

Nota:
- Puedes encontrar la clave API en la configuración del plugin de Obsidian (Ajustes > Local REST API > Seguridad)
- El puerto predeterminado es 27123
- El host predeterminado es 127.0.0.1 (localhost)

## Inicio Rápido

### Instalación

#### Obsidian REST API

Necesitas tener el plugin comunitario Obsidian REST API ejecutándose: https://github.com/coddingtonbear/obsidian-local-rest-api

Instálalo y habilítalo en los ajustes y copia la clave API.

#### Claude Desktop

En MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

En Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Configuración de Servidores de Desarrollo/No Publicados</summary>

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/pyobsidianmcp",
        "run",
        "pyobsidianmcp"
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
  <summary>Instalar desde GitHub (uvx)</summary>

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/rmc8/PyObsidianMCP",
        "pyobsidianmcp"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>"
      }
    }
  }
}
```
</details>

## Desarrollo

### Construcción

Para preparar el paquete para distribución:

1. Sincronizar dependencias y actualizar el archivo de bloqueo:
```bash
uv sync
```

### Depuración

Dado que los servidores MCP se ejecutan sobre stdio, la depuración puede ser desafiante. Para la mejor experiencia de depuración, recomendamos encarecidamente usar el [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

Puedes lanzar el MCP Inspector a través de `npx` con este comando:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/pyobsidianmcp run pyobsidianmcp
```

Al lanzarlo, el Inspector mostrará una URL que puedes acceder en tu navegador para comenzar a depurar.

También puedes ver los logs del servidor (si están configurados) o usar el logging estándar de Python.
