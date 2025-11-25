🌐 **Language / 言語**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/commits)

# PyObsidianMCP

Servidor MCP para interagir com o Obsidian através do plugin comunitário Local REST API.

## Componentes

### Ferramentas

O servidor implementa múltiplas ferramentas para interagir com o Obsidian:

| Ferramenta | Descrição |
|------------|-----------|
| `list_notes` | Lista todas as notas no vault ou em um diretório específico |
| `read_note` | Lê o conteúdo de uma nota específica |
| `search_notes` | Pesquisa notas contendo texto específico |
| `create_note` | Cria uma nova nota com frontmatter opcional |
| `update_note` | Atualiza (substitui) o conteúdo completo de uma nota |
| `append_note` | Adiciona conteúdo ao final de uma nota |
| `delete_note` | Exclui uma nota do vault |
| `patch_note` | Atualiza uma seção específica (título/bloco/frontmatter) |
| `list_commands` | Lista todos os comandos do Obsidian disponíveis |
| `execute_command` | Executa um comando do Obsidian |
| `batch_read_notes` | Lê múltiplas notas de uma vez |
| `complex_search` | Pesquisa com consultas JsonLogic para filtragem avançada |
| `get_recent_changes` | Obtém arquivos modificados recentemente (requer plugin Dataview) |
| `get_periodic_note` | Obtém a nota diária/semanal/mensal de hoje (requer plugin Periodic Notes) |
| `get_recent_periodic_notes` | Obtém notas periódicas recentes |
| `open_note` | Abre uma nota na interface do Obsidian |
| `get_active_note` | Obtém a nota atualmente ativa |
| `update_active_note` | Atualiza o conteúdo da nota ativa |
| `append_active_note` | Adiciona conteúdo à nota ativa |

### Exemplos de prompts

É bom primeiro instruir o Claude a usar o Obsidian. Então ele sempre chamará a ferramenta.

Você pode usar prompts como estes:
- "Liste todas as notas na pasta 'Daily'"
- "Pesquise todas as notas que mencionam 'Projeto X' e resuma-as"
- "Crie uma nova nota chamada 'Notas da Reunião' com o conteúdo da nossa discussão"
- "Adicione 'TODO: Revisar PR' à minha nota diária"
- "Obtenha o conteúdo da nota ativa e critique-o"
- "Encontre todos os arquivos markdown na pasta Work usando complex search"

## Configuração

### Chave API do Obsidian REST

Existem duas formas de configurar o ambiente com a chave API do Obsidian REST.

1. Adicionar à configuração do servidor (recomendado)

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

2. Criar um arquivo `.env` no diretório de trabalho com as seguintes variáveis obrigatórias:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123
```

Nota:
- Você pode encontrar a chave API na configuração do plugin do Obsidian (Configurações > Local REST API > Segurança)
- A porta padrão é 27123
- O host padrão é 127.0.0.1 (localhost)

## Início Rápido

### Instalação

#### Obsidian REST API

Você precisa ter o plugin comunitário Obsidian REST API em execução: https://github.com/coddingtonbear/obsidian-local-rest-api

Instale e habilite-o nas configurações e copie a chave API.

#### Claude Desktop

No MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

No Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Configuração de Servidores de Desenvolvimento/Não Publicados</summary>

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
  <summary>Instalar do GitHub (uvx)</summary>

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

## Desenvolvimento

### Construção

Para preparar o pacote para distribuição:

1. Sincronizar dependências e atualizar o arquivo de bloqueio:
```bash
uv sync
```

### Depuração

Como os servidores MCP são executados via stdio, a depuração pode ser desafiadora. Para a melhor experiência de depuração, recomendamos fortemente usar o [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

Você pode iniciar o MCP Inspector via `npx` com este comando:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/pyobsidianmcp run pyobsidianmcp
```

Ao iniciar, o Inspector exibirá uma URL que você pode acessar no seu navegador para começar a depurar.

Você também pode verificar os logs do servidor (se configurados) ou usar o logging padrão do Python.
