🌐 **Language / 言語**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/commits)

# PyObsidianMCP

通过 Local REST API 社区插件与 Obsidian 交互的 MCP 服务器。

## 组件

### 工具

服务器实现了多个与 Obsidian 交互的工具：

| 工具 | 描述 |
|------|------|
| `list_notes` | 列出保险库或特定目录中的所有笔记 |
| `read_note` | 读取特定笔记的内容 |
| `search_notes` | 搜索包含特定文本的笔记 |
| `create_note` | 创建带有可选 frontmatter 的新笔记 |
| `update_note` | 更新（替换）笔记的全部内容 |
| `append_note` | 在笔记末尾追加内容 |
| `delete_note` | 从保险库中删除笔记 |
| `patch_note` | 更新特定部分（标题/块/frontmatter） |
| `list_commands` | 列出所有可用的 Obsidian 命令 |
| `execute_command` | 执行 Obsidian 命令 |
| `batch_read_notes` | 一次读取多个笔记 |
| `complex_search` | 使用 JsonLogic 查询进行高级过滤搜索 |
| `get_recent_changes` | 获取最近修改的文件（需要 Dataview 插件） |
| `get_periodic_note` | 获取今天的日记/周记/月记（需要 Periodic Notes 插件） |
| `get_recent_periodic_notes` | 获取最近的周期性笔记 |
| `open_note` | 在 Obsidian UI 中打开笔记 |
| `get_active_note` | 获取当前活动的笔记 |
| `update_active_note` | 更新活动笔记的内容 |
| `append_active_note` | 向活动笔记追加内容 |
| `vector_search` | 使用自然语言进行语义搜索（需要 vector extras） |
| `find_similar_notes` | 查找与指定笔记相似的笔记（需要 vector extras） |
| `vector_status` | 获取向量搜索索引的状态（需要 vector extras） |

### 示例提示

首先最好指示 Claude 使用 Obsidian。这样它就会一直调用工具。

你可以使用这样的提示：
- "列出'Daily'文件夹中的所有笔记"
- "搜索所有提到'项目X'的笔记并总结"
- "用我们讨论的内容创建一个名为'会议记录'的新笔记"
- "在我的日记中追加'TODO: 审查PR'"
- "获取活动笔记的内容并进行评论"
- "使用 complex search 查找 Work 文件夹中的所有 markdown 文件"
- "使用语义搜索查找关于机器学习的笔记"
- "查找与我的项目计划相似的笔记"

## 配置

### Obsidian REST API 密钥

有两种方法可以配置 Obsidian REST API 密钥的环境。

1. 添加到服务器配置（推荐）

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

2. 在工作目录中创建包含以下必需变量的 `.env` 文件：

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123
```

注意：
- 你可以在 Obsidian 插件配置中找到 API 密钥（设置 > Local REST API > 安全）
- 默认端口是 27123
- 默认主机是 127.0.0.1（localhost）

## 快速开始

### 安装

#### Obsidian REST API

你需要运行 Obsidian REST API 社区插件：https://github.com/coddingtonbear/obsidian-local-rest-api

在设置中安装并启用它，然后复制 API 密钥。

#### Claude Desktop

MacOS：`~/Library/Application\ Support/Claude/claude_desktop_config.json`

Windows：`%APPDATA%/Claude/claude_desktop_config.json`

**推荐：从 PyPI 安装（uvx）**

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
  <summary>开发/未发布服务器配置</summary>

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
  <summary>从 GitHub 安装（uvx）</summary>

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

## 向量搜索（可选）

使用 ChromaDB 的语义搜索功能。此功能允许在整个保险库中进行自然语言查询。

### 安装

```bash
# 基础（本地嵌入 - 无需 API 密钥）
pip install "py-obsidian-tools[vector]"

# 使用外部嵌入提供商
pip install "py-obsidian-tools[vector-openai]"
pip install "py-obsidian-tools[vector-google]"
pip install "py-obsidian-tools[vector-cohere]"
pip install "py-obsidian-tools[vector-all]"
```

### 创建索引

在使用向量搜索之前，你需要创建保险库的索引：

```bash
# 方法 1：已安装的情况下
pyobsidian-index full --verbose

# 方法 2：使用 uvx（无需安装）
uvx --from py-obsidian-tools pyobsidian-index full --verbose
```

### CLI 命令

| 命令 | 描述 |
|------|------|
| `pyobsidian-index full` | 索引保险库中的所有笔记 |
| `pyobsidian-index update` | 增量更新（仅新建/修改的笔记） |
| `pyobsidian-index clear` | 清除整个索引 |
| `pyobsidian-index status` | 显示索引状态 |

### 环境变量

```bash
VECTOR_PROVIDER=default          # default, ollama, openai, google, cohere
VECTOR_CHROMA_PATH=~/.obsidian-vector
VECTOR_CHUNK_SIZE=512

# Ollama
VECTOR_OLLAMA_HOST=http://localhost:11434
VECTOR_OLLAMA_MODEL=nomic-embed-text

# OpenAI
VECTOR_OPENAI_API_KEY=sk-xxx
VECTOR_OPENAI_MODEL=text-embedding-3-small

# Google
VECTOR_GOOGLE_API_KEY=xxx
VECTOR_GOOGLE_MODEL=embedding-001

# Cohere
VECTOR_COHERE_API_KEY=xxx
VECTOR_COHERE_MODEL=embed-multilingual-v3.0
```

### 嵌入提供商

| 提供商 | 模型 | 最适合 |
|--------|------|--------|
| default | all-MiniLM-L6-v2 | 快速、免费、完全本地 |
| ollama | nomic-embed-text | 高质量、本地 |
| openai | text-embedding-3-small | 最高质量、多语言 |
| google | embedding-001 | Google AI 集成 |
| cohere | embed-multilingual-v3.0 | 多语言专业 |

## 开发

### 构建

准备分发包：

1. 同步依赖项并更新锁定文件：
```bash
uv sync
```

### 调试

由于 MCP 服务器通过 stdio 运行，调试可能具有挑战性。为了获得最佳调试体验，我们强烈建议使用 [MCP Inspector](https://github.com/modelcontextprotocol/inspector)。

你可以使用以下命令通过 `npx` 启动 MCP Inspector：

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/py-obsidian-tools run py-obsidian-tools
```

启动后，Inspector 将显示一个可以在浏览器中访问以开始调试的 URL。

你也可以查看服务器日志（如果已配置）或使用标准 Python 日志记录。
