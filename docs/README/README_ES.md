🌐 **Language / 言語**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/commits)

# py-obsidian-tools

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
| `open_note` | Abre una nota en la interfaz de Obsidian |
| `get_active_note` | Obtiene la nota actualmente activa |
| `update_active_note` | Actualiza el contenido de la nota activa |
| `append_active_note` | Añade contenido a la nota activa |
| `patch_active_note` | Actualiza una sección específica de la nota activa |
| `delete_active_note` | Elimina la nota actualmente activa |
| `server_status` | Obtiene el estado del servidor Obsidian Local REST API |
| `dataview_query` | Ejecuta consultas Dataview DQL (requiere plugin Dataview) |
| `vector_search` | Búsqueda semántica usando lenguaje natural (requiere vector extras) |
| `find_similar_notes` | Encuentra notas similares a una nota especificada (requiere vector extras) |
| `vector_status` | Obtiene el estado del índice de búsqueda vectorial (requiere vector extras) |

### Ejemplos de prompts

Es bueno primero indicarle a Claude que use Obsidian. Entonces siempre llamará a la herramienta.

Puedes usar prompts como estos:
- "Lista todas las notas en la carpeta 'Daily'"
- "Busca todas las notas que mencionen 'Proyecto X' y resúmelas"
- "Crea una nueva nota llamada 'Notas de Reunión' con el contenido de nuestra discusión"
- "Añade 'TODO: Revisar PR' a mi nota diaria"
- "Obtén el contenido de la nota activa y critícalo"
- "Encuentra todos los archivos markdown en la carpeta Work usando complex search"
- "Busca notas sobre aprendizaje automático usando búsqueda semántica"
- "Encuentra notas similares a mi plan de proyecto"

## Configuración

### Clave API de Obsidian REST

Hay dos formas de configurar el entorno con la clave API de Obsidian REST.

1. Añadir a la configuración del servidor (recomendado)

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

2. Crear un archivo `.env` en el directorio de trabajo con las siguientes variables requeridas:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27124
```

Nota:
- Puedes encontrar la clave API en la configuración del plugin de Obsidian (Ajustes > Local REST API > Seguridad)
- El puerto predeterminado es 27124
- El host predeterminado es 127.0.0.1 (localhost)

## Inicio Rápido

### Instalación

#### Obsidian REST API

Necesitas tener el plugin comunitario Obsidian REST API ejecutándose: https://github.com/coddingtonbear/obsidian-local-rest-api

Instálalo y habilítalo en los ajustes y copia la clave API.

#### Claude Desktop

En MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

En Windows: `%APPDATA%/Claude/claude_desktop_config.json`

**Recomendado: Instalar desde PyPI (uvx)**

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
  <summary>Configuración de Servidores de Desarrollo/No Publicados</summary>

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
  <summary>Instalar desde GitHub (uvx)</summary>

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

## Búsqueda Vectorial

La funcionalidad de búsqueda semántica usando ChromaDB está incluida por defecto. Esta característica permite consultas en lenguaje natural en todo tu vault.

> **Nota**: Las dependencias de búsqueda vectorial (chromadb, semantic-text-splitter) ahora están incluidas como dependencias requeridas. ¡No se necesitan extras para el uso básico!

### Instalación CLI

**Usando uvx (recomendado)**:

```bash
# Sin instalación requerida - ejecutar directamente con uvx
uvx --from py-obsidian-tools pyobsidian-index full --verbose

# Con proveedores de embeddings externos
uvx --from 'py-obsidian-tools[vector-openai]' pyobsidian-index full --verbose
uvx --from 'py-obsidian-tools[vector-google]' pyobsidian-index full --verbose
uvx --from 'py-obsidian-tools[vector-cohere]' pyobsidian-index full --verbose
```

**Usando uv (para desarrollo)**:

```bash
# Básico (embeddings locales - no requiere API key)
uv sync

# Con proveedores de embeddings externos
uv sync --extra vector-openai
uv sync --extra vector-google
uv sync --extra vector-cohere
uv sync --extra vector-all

# Ejecutar indexador
uv run pyobsidian-index full --verbose
```

**Usando pip**:

```bash
# Básico (embeddings locales - no requiere API key)
pip install py-obsidian-tools

# Con proveedores de embeddings externos
pip install "py-obsidian-tools[vector-openai]"
pip install "py-obsidian-tools[vector-google]"
pip install "py-obsidian-tools[vector-cohere]"
pip install "py-obsidian-tools[vector-all]"
```

### Crear Índice

Antes de usar la búsqueda vectorial, necesitas crear un índice de tu vault:

```bash
# Usando uvx (recomendado - sin instalación requerida)
uvx --from py-obsidian-tools pyobsidian-index full --verbose

# Usando uv (para desarrollo)
uv run pyobsidian-index full --verbose

# O si está instalado via pip
pyobsidian-index full --verbose
```

### Comandos CLI

```bash
# Usando uvx
uvx --from py-obsidian-tools pyobsidian-index <comando>

# Usando uv (para desarrollo)
uv run pyobsidian-index <comando>

# Usando instalación pip
pyobsidian-index <comando>
```

| Comando | Descripción |
|---------|-------------|
| `full` | Indexar todas las notas del vault |
| `update` | Actualización incremental (solo notas nuevas/modificadas) |
| `clear` | Limpiar todo el índice |
| `status` | Mostrar estado del índice |

### Variables de Entorno

```bash
VECTOR_PROVIDER=default          # default, ollama, openai, google, cohere
VECTOR_CHROMA_PATH=~/.obsidian-vector
VECTOR_CHUNK_SIZE=512

# Para Ollama
VECTOR_OLLAMA_HOST=http://localhost:11434
VECTOR_OLLAMA_MODEL=nomic-embed-text

# Para OpenAI
VECTOR_OPENAI_API_KEY=sk-xxx
VECTOR_OPENAI_MODEL=text-embedding-3-small

# Para Google
VECTOR_GOOGLE_API_KEY=xxx
VECTOR_GOOGLE_MODEL=embedding-001

# Para Cohere
VECTOR_COHERE_API_KEY=xxx
VECTOR_COHERE_MODEL=embed-multilingual-v3.0
```

### Proveedores de Embeddings

| Proveedor | Modelo | Mejor Para |
|-----------|--------|------------|
| default | all-MiniLM-L6-v2 | Rápido, gratuito, completamente local |
| ollama | nomic-embed-text | Alta calidad, local |
| openai | text-embedding-3-small | Mejor calidad, multilingüe |
| google | embedding-001 | Integración Google AI |
| cohere | embed-multilingual-v3.0 | Especialización multilingüe |

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
npx @modelcontextprotocol/inspector uv --directory /path/to/py-obsidian-tools run py-obsidian-tools
```

Al lanzarlo, el Inspector mostrará una URL que puedes acceder en tu navegador para comenzar a depurar.

También puedes ver los logs del servidor (si están configurados) o usar el logging estándar de Python.
