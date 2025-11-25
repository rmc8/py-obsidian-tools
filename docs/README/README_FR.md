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
| `vector_search` | Recherche sémantique en langage naturel (nécessite vector extras) |
| `find_similar_notes` | Trouve des notes similaires à une note spécifiée (nécessite vector extras) |
| `vector_status` | Obtient l'état de l'index de recherche vectorielle (nécessite vector extras) |

### Exemples de prompts

Il est bon d'abord d'indiquer à Claude d'utiliser Obsidian. Ensuite, il appellera toujours l'outil.

Vous pouvez utiliser des prompts comme ceux-ci :
- « Liste toutes les notes dans le dossier 'Daily' »
- « Recherche toutes les notes mentionnant 'Projet X' et résume-les »
- « Crée une nouvelle note appelée 'Notes de Réunion' avec le contenu de notre discussion »
- « Ajoute 'TODO: Réviser PR' à ma note quotidienne »
- « Obtiens le contenu de la note active et critique-le »
- « Trouve tous les fichiers markdown dans le dossier Work en utilisant complex search »
- « Recherche des notes sur l'apprentissage automatique en utilisant la recherche sémantique »
- « Trouve des notes similaires à mon plan de projet »

## Configuration

### Clé API Obsidian REST

Il y a deux façons de configurer l'environnement avec la clé API Obsidian REST.

1. Ajouter à la configuration du serveur (recommandé)

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["py-obsidian-tools"],
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

**Recommandé : Installer depuis PyPI (uvx)**

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["py-obsidian-tools"],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27123"
      }
    }
  }
}
```

<details>
  <summary>Configuration des Serveurs de Développement/Non Publiés</summary>

```json
{
  "mcpServers": {
    "obsidian": {
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
  <summary>Installer depuis GitHub (uvx)</summary>

```json
{
  "mcpServers": {
    "obsidian": {
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

## Recherche Vectorielle (Optionnel)

Fonctionnalité de recherche sémantique utilisant ChromaDB. Cette fonctionnalité permet des requêtes en langage naturel sur l'ensemble de votre coffre.

### Installation

```bash
# Basique (embeddings locaux - pas de clé API requise)
pip install "py-obsidian-tools[vector]"

# Avec fournisseurs d'embeddings externes
pip install "py-obsidian-tools[vector-openai]"
pip install "py-obsidian-tools[vector-google]"
pip install "py-obsidian-tools[vector-cohere]"
pip install "py-obsidian-tools[vector-all]"
```

### Créer l'Index

Avant d'utiliser la recherche vectorielle, vous devez créer un index de votre coffre :

```bash
# Méthode 1 : Si déjà installé
pyobsidian-index full --verbose

# Méthode 2 : Utiliser uvx (aucune installation requise)
uvx --from py-obsidian-tools pyobsidian-index full --verbose
```

### Commandes CLI

| Commande | Description |
|----------|-------------|
| `pyobsidian-index full` | Indexer toutes les notes du coffre |
| `pyobsidian-index update` | Mise à jour incrémentale (uniquement notes nouvelles/modifiées) |
| `pyobsidian-index clear` | Effacer l'index entier |
| `pyobsidian-index status` | Afficher l'état de l'index |

### Variables d'Environnement

```bash
VECTOR_PROVIDER=default          # default, ollama, openai, google, cohere
VECTOR_CHROMA_PATH=~/.obsidian-vector
VECTOR_CHUNK_SIZE=512

# Pour Ollama
VECTOR_OLLAMA_HOST=http://localhost:11434
VECTOR_OLLAMA_MODEL=nomic-embed-text

# Pour OpenAI
VECTOR_OPENAI_API_KEY=sk-xxx
VECTOR_OPENAI_MODEL=text-embedding-3-small

# Pour Google
VECTOR_GOOGLE_API_KEY=xxx
VECTOR_GOOGLE_MODEL=embedding-001

# Pour Cohere
VECTOR_COHERE_API_KEY=xxx
VECTOR_COHERE_MODEL=embed-multilingual-v3.0
```

### Fournisseurs d'Embeddings

| Fournisseur | Modèle | Idéal Pour |
|-------------|--------|------------|
| default | all-MiniLM-L6-v2 | Rapide, gratuit, entièrement local |
| ollama | nomic-embed-text | Haute qualité, local |
| openai | text-embedding-3-small | Meilleure qualité, multilingue |
| google | embedding-001 | Intégration Google AI |
| cohere | embed-multilingual-v3.0 | Spécialisation multilingue |

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
npx @modelcontextprotocol/inspector uv --directory /path/to/py-obsidian-tools run py-obsidian-tools
```

Au lancement, l'Inspector affichera une URL que vous pouvez accéder dans votre navigateur pour commencer le débogage.

Vous pouvez également consulter les logs du serveur (s'ils sont configurés) ou utiliser le logging standard de Python.
