🌐 **Language / 語言**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/commits)

# py-obsidian-tools

透過 Local REST API 社群外掛與 Obsidian 互動的 MCP 伺服器。

## 元件

### 工具

伺服器實作了多個與 Obsidian 互動的工具：

| 工具 | 說明 |
|------|------|
| `list_notes` | 列出保險庫或特定目錄中的所有筆記 |
| `read_note` | 讀取特定筆記的內容 |
| `search_notes` | 搜尋包含特定文字的筆記 |
| `create_note` | 建立帶有可選 frontmatter 的新筆記 |
| `update_note` | 更新（取代）筆記的全部內容 |
| `append_note` | 在筆記末尾附加內容 |
| `delete_note` | 從保險庫中刪除筆記 |
| `patch_note` | 更新特定區段（標題/區塊/frontmatter） |
| `list_commands` | 列出所有可用的 Obsidian 指令 |
| `execute_command` | 執行 Obsidian 指令 |
| `batch_read_notes` | 一次讀取多個筆記 |
| `complex_search` | 使用 JsonLogic 查詢進行進階篩選搜尋 |
| `get_recent_changes` | 取得最近修改的檔案（需要 Dataview 外掛） |
| `get_periodic_note` | 取得今天的日記/週記/月記（需要 Periodic Notes 外掛） |
| `open_note` | 在 Obsidian UI 中開啟筆記 |
| `get_active_note` | 取得目前活動的筆記 |
| `update_active_note` | 更新活動筆記的內容 |
| `append_active_note` | 向活動筆記附加內容 |
| `patch_active_note` | 更新活動筆記的特定區段 |
| `delete_active_note` | 刪除目前活動的筆記 |
| `server_status` | 取得 Obsidian Local REST API 伺服器狀態 |
| `dataview_query` | 執行 Dataview DQL 查詢（需要 Dataview 外掛） |
| `vector_search` | 使用自然語言進行語意搜尋（需要 vector extras） |
| `find_similar_notes` | 尋找與指定筆記相似的筆記（需要 vector extras） |
| `vector_status` | 取得向量搜尋索引的狀態（需要 vector extras） |

### 範例提示

首先最好指示 Claude 使用 Obsidian。這樣它就會一直呼叫工具。

您可以使用這樣的提示：
- 「列出『Daily』資料夾中的所有筆記」
- 「搜尋所有提到『專案X』的筆記並總結」
- 「用我們討論的內容建立一個名為『會議記錄』的新筆記」
- 「在我的日記中附加『TODO: 審查PR』」
- 「取得活動筆記的內容並進行評論」
- 「使用 complex search 尋找 Work 資料夾中的所有 markdown 檔案」
- 「使用語意搜尋尋找關於機器學習的筆記」
- 「尋找與我的專案計劃相似的筆記」

## 設定

### Obsidian REST API 金鑰

有兩種方法可以設定 Obsidian REST API 金鑰的環境。

1. 新增到伺服器設定（建議）

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

2. 在工作目錄中建立包含以下必要變數的 `.env` 檔案：

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27124
```

注意：
- 您可以在 Obsidian 外掛設定中找到 API 金鑰（設定 > Local REST API > 安全性）
- 預設連接埠是 27124
- 預設主機是 127.0.0.1（localhost）

## 快速開始

### 安裝

#### Obsidian REST API

您需要執行 Obsidian REST API 社群外掛：https://github.com/coddingtonbear/obsidian-local-rest-api

在設定中安裝並啟用它，然後複製 API 金鑰。

#### Claude Desktop

MacOS：`~/Library/Application\ Support/Claude/claude_desktop_config.json`

Windows：`%APPDATA%/Claude/claude_desktop_config.json`

**建議：從 PyPI 安裝（uvx）**

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
  <summary>開發/未發布伺服器設定</summary>

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
  <summary>從 GitHub 安裝（uvx）</summary>

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

## 向量搜尋（選用）

使用 ChromaDB 的語意搜尋功能。此功能允許在整個保險庫中進行自然語言查詢。

### 安裝

```bash
# 基礎（本地嵌入 - 無需 API 金鑰）
pip install "py-obsidian-tools[vector]"

# 使用外部嵌入提供商
pip install "py-obsidian-tools[vector-openai]"
pip install "py-obsidian-tools[vector-google]"
pip install "py-obsidian-tools[vector-cohere]"
pip install "py-obsidian-tools[vector-all]"
```

### 建立索引

在使用向量搜尋之前，您需要建立保險庫的索引：

```bash
# 方法 1：已安裝的情況下
pyobsidian-index full --verbose

# 方法 2：使用 uvx（無需安裝）
uvx --from py-obsidian-tools pyobsidian-index full --verbose
```

### CLI 指令

| 指令 | 說明 |
|------|------|
| `pyobsidian-index full` | 索引保險庫中的所有筆記 |
| `pyobsidian-index update` | 增量更新（僅新建/修改的筆記） |
| `pyobsidian-index clear` | 清除整個索引 |
| `pyobsidian-index status` | 顯示索引狀態 |

### 環境變數

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

| 提供商 | 模型 | 最適合 |
|--------|------|--------|
| default | all-MiniLM-L6-v2 | 快速、免費、完全本地 |
| ollama | nomic-embed-text | 高品質、本地 |
| openai | text-embedding-3-small | 最高品質、多語言 |
| google | embedding-001 | Google AI 整合 |
| cohere | embed-multilingual-v3.0 | 多語言專業 |

## 開發

### 建置

準備發布套件：

1. 同步相依性並更新鎖定檔案：
```bash
uv sync
```

### 除錯

由於 MCP 伺服器透過 stdio 執行，除錯可能具有挑戰性。為了獲得最佳除錯體驗，我們強烈建議使用 [MCP Inspector](https://github.com/modelcontextprotocol/inspector)。

您可以使用以下指令透過 `npx` 啟動 MCP Inspector：

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/py-obsidian-tools run py-obsidian-tools
```

啟動後，Inspector 將顯示一個可以在瀏覽器中存取以開始除錯的 URL。

您也可以檢視伺服器日誌（如果已設定）或使用標準 Python 日誌記錄。
