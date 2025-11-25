🌐 **Language / 言語**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/commits)

# PyObsidianMCP

Serveur MCP pour interagir avec Obsidian via le plugin communautaire Local REST API.

## Composants

### Outils

Le serveur implémente plusieurs outils pour interagir avec Obsidian :

| Outil | Description |
|-------|-------------|
| `list_notes` | Liste toutes les notes dans le coffre ou un répertoire spécifique |
| `read_note` | Lit le contenu d'une note spécifique |
| `search_notes` | Recherche des notes contenant un texte spécifique |
| `create_note` | Crée une nouvelle note avec frontmatter optionnel |
| `update_note` | Met à jour (remplace) le contenu entier d'une note |
| `append_note` | Ajoute du contenu à la fin d'une note |
| `delete_note` | Supprime une note du coffre |
| `patch_note` | Met à jour une section spécifique (titre/bloc/frontmatter) |
| `list_commands` | Liste toutes les commandes Obsidian disponibles |
| `execute_command` | Exécute une commande Obsidian |
| `batch_read_notes` | Lit plusieurs notes à la fois |
| `complex_search` | Recherche avec requêtes JsonLogic pour filtrage avancé |
| `get_recent_changes` | Obtient les fichiers récemment modifiés (nécessite le plugin Dataview) |
| `get_periodic_note` | Obtient la note quotidienne/hebdomadaire/mensuelle d'aujourd'hui (nécessite le plugin Periodic Notes) |
| `get_recent_periodic_notes` | Obtient les notes périodiques récentes |
| `open_note` | Ouvre une note dans l'interface d'Obsidian |
| `get_active_note` | Obtient la note actuellement active |
| `update_active_note` | Met à jour le contenu de la note active |
| `append_active_note` | Ajoute du contenu à la note active |

### Exemples de prompts

Il est bon d'abord d'indiquer à Claude d'utiliser Obsidian. Ensuite, il appellera toujours l'outil.

Vous pouvez utiliser des prompts comme ceux-ci :
- « Liste toutes les notes dans le dossier 'Daily' »
- « Recherche toutes les notes mentionnant 'Projet X' et résume-les »
- « Crée une nouvelle note appelée 'Notes de Réunion' avec le contenu de notre discussion »
- « Ajoute 'TODO: Réviser PR' à ma note quotidienne »
- « Obtiens le contenu de la note active et critique-le »
- « Trouve tous les fichiers markdown dans le dossier Work en utilisant complex search »

## Configuration

### Clé API Obsidian REST

Il y a deux façons de configurer l'environnement avec la clé API Obsidian REST.

1. Ajouter à la configuration du serveur (recommandé)

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

2. Créer un fichier `.env` dans le répertoire de travail avec les variables requises suivantes :

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123
```

Note :
- Vous pouvez trouver la clé API dans la configuration du plugin Obsidian (Paramètres > Local REST API > Sécurité)
- Le port par défaut est 27123
- L'hôte par défaut est 127.0.0.1 (localhost)

## Démarrage Rapide

### Installation

#### Obsidian REST API

Vous devez avoir le plugin communautaire Obsidian REST API en cours d'exécution : https://github.com/coddingtonbear/obsidian-local-rest-api

Installez-le et activez-le dans les paramètres et copiez la clé API.

#### Claude Desktop

Sur MacOS : `~/Library/Application\ Support/Claude/claude_desktop_config.json`

Sur Windows : `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Configuration des Serveurs de Développement/Non Publiés</summary>

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
  <summary>Installer depuis GitHub (uvx)</summary>

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

## Développement

### Construction

Pour préparer le paquet pour la distribution :

1. Synchroniser les dépendances et mettre à jour le fichier de verrouillage :
```bash
uv sync
```

### Débogage

Comme les serveurs MCP s'exécutent via stdio, le débogage peut être difficile. Pour la meilleure expérience de débogage, nous recommandons fortement d'utiliser le [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

Vous pouvez lancer le MCP Inspector via `npx` avec cette commande :

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/pyobsidianmcp run pyobsidianmcp
```

Au lancement, l'Inspector affichera une URL que vous pouvez accéder dans votre navigateur pour commencer le débogage.

Vous pouvez également consulter les logs du serveur (s'ils sont configurés) ou utiliser le logging standard de Python.
