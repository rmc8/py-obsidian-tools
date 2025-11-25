🌐 **Language / 言語**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/commits)

# py-obsidian-tools

Local REST APIコミュニティプラグインを介してObsidianと連携するMCPサーバーです。

## コンポーネント

### ツール

サーバーはObsidianと連携するための複数のツールを実装しています：

| ツール | 説明 |
|--------|------|
| `list_notes` | Vault内または特定のディレクトリ内のすべてのノートを一覧表示 |
| `read_note` | 特定のノートの内容を読み取り |
| `search_notes` | 特定のテキストを含むノートを検索 |
| `create_note` | オプションのフロントマター付きで新しいノートを作成 |
| `update_note` | ノートの全内容を更新（置換） |
| `append_note` | ノートの末尾にコンテンツを追加 |
| `delete_note` | Vaultからノートを削除 |
| `patch_note` | 特定のセクション（見出し/ブロック/フロントマター）を更新 |
| `list_commands` | 利用可能なすべてのObsidianコマンドを一覧表示 |
| `execute_command` | Obsidianコマンドを実行 |
| `batch_read_notes` | 複数のノートを一度に読み取り |
| `complex_search` | JsonLogicクエリを使用した高度なフィルタリング検索 |
| `get_recent_changes` | 最近変更されたファイルを取得（Dataviewプラグインが必要） |
| `get_periodic_note` | 今日のデイリー/ウィークリー/マンスリーノートを取得（Periodic Notesプラグインが必要） |
| `open_note` | ObsidianのUIでノートを開く |
| `get_active_note` | 現在アクティブなノートを取得 |
| `update_active_note` | アクティブなノートの内容を更新 |
| `append_active_note` | アクティブなノートにコンテンツを追加 |
| `patch_active_note` | アクティブなノートの特定セクションを更新 |
| `delete_active_note` | 現在アクティブなノートを削除 |
| `server_status` | Obsidian Local REST APIサーバーの状態を取得 |
| `dataview_query` | Dataview DQLクエリを実行（Dataviewプラグインが必要） |
| `vector_search` | 自然言語を使用したセマンティック検索（vector extrasが必要） |
| `find_similar_notes` | 指定したノートに類似したノートを検索（vector extrasが必要） |
| `vector_status` | ベクトル検索インデックスの状態を取得（vector extrasが必要） |

### プロンプト例

まずClaudeにObsidianを使うように指示すると良いでしょう。そうすれば常にツールを呼び出します。

以下のようなプロンプトを使用できます：
- 「'Daily'フォルダ内のすべてのノートをリストして」
- 「'プロジェクトX'に言及しているすべてのノートを検索して要約して」
- 「私たちの議論の内容で'会議メモ'という新しいノートを作成して」
- 「デイリーノートに'TODO: PRをレビュー'を追記して」
- 「アクティブなノートの内容を取得して批評して」
- 「complex searchを使用してWorkフォルダ内のすべてのmarkdownファイルを検索して」
- 「セマンティック検索を使用して機械学習に関するノートを検索して」
- 「私のプロジェクト計画に似ているノートを探して」
- 「Dataviewクエリを実行して#projectタグを持つすべてのノートを一覧表示して」
- 「今日のデイリーノートを取得して」
- 「アクティブなノートの'タスク'セクションを更新して」
- 「Obsidian APIサーバーの状態を確認して」

## 設定

### Obsidian REST APIキー

Obsidian REST APIキーで環境を設定する方法は2つあります。

1. サーバー設定に追加（推奨）

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

2. 作業ディレクトリに以下の必須変数を含む`.env`ファイルを作成：

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27124
```

注意：
- APIキーはObsidianのプラグイン設定（設定 > Local REST API > セキュリティ）で確認できます
- デフォルトポートは27124です
- デフォルトホストは127.0.0.1（localhost）です

## クイックスタート

### インストール

#### Obsidian REST API

Obsidian REST APIコミュニティプラグインが実行されている必要があります：https://github.com/coddingtonbear/obsidian-local-rest-api

設定でインストールして有効にし、APIキーをコピーしてください。

#### Claude Desktop

MacOSの場合：`~/Library/Application\ Support/Claude/claude_desktop_config.json`

Windowsの場合：`%APPDATA%/Claude/claude_desktop_config.json`

**推奨：PyPIからインストール（uvx）**

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
  <summary>開発/未公開サーバー設定</summary>

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
  <summary>GitHubからインストール（uvx）</summary>

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

## ベクトル検索（オプション）

ChromaDBを使用したセマンティック検索機能です。この機能により、Vault全体で自然言語クエリが可能になります。

### インストール

```bash
# 基本（ローカル埋め込み - APIキー不要）
pip install "py-obsidian-tools[vector]"

# 外部埋め込みプロバイダーを使用する場合
pip install "py-obsidian-tools[vector-openai]"
pip install "py-obsidian-tools[vector-google]"
pip install "py-obsidian-tools[vector-cohere]"
pip install "py-obsidian-tools[vector-all]"
```

### インデックスの作成

ベクトル検索を使用する前に、Vaultのインデックスを作成する必要があります：

```bash
# 方法1：インストール済みの場合
pyobsidian-index full --verbose

# 方法2：uvxを使用（インストール不要）
uvx --from py-obsidian-tools pyobsidian-index full --verbose
```

### CLIコマンド

| コマンド | 説明 |
|---------|------|
| `pyobsidian-index full` | Vault内のすべてのノートをインデックス |
| `pyobsidian-index update` | 差分更新（新規/変更されたノートのみ） |
| `pyobsidian-index clear` | インデックス全体をクリア |
| `pyobsidian-index status` | インデックスの状態を表示 |

### 環境変数

```bash
VECTOR_PROVIDER=default          # default, ollama, openai, google, cohere
VECTOR_CHROMA_PATH=~/.obsidian-vector
VECTOR_CHUNK_SIZE=512

# Ollama用
VECTOR_OLLAMA_HOST=http://localhost:11434
VECTOR_OLLAMA_MODEL=nomic-embed-text

# OpenAI用
VECTOR_OPENAI_API_KEY=sk-xxx
VECTOR_OPENAI_MODEL=text-embedding-3-small

# Google用
VECTOR_GOOGLE_API_KEY=xxx
VECTOR_GOOGLE_MODEL=embedding-001

# Cohere用
VECTOR_COHERE_API_KEY=xxx
VECTOR_COHERE_MODEL=embed-multilingual-v3.0
```

### 埋め込みプロバイダー

| プロバイダー | モデル | 用途 |
|-------------|--------|------|
| default | all-MiniLM-L6-v2 | 高速、無料、完全ローカル |
| ollama | nomic-embed-text | 高品質、ローカル |
| openai | text-embedding-3-small | 最高品質、多言語 |
| google | embedding-001 | Google AI連携 |
| cohere | embed-multilingual-v3.0 | 多言語特化 |

## 開発

### ビルド

パッケージを配布用に準備するには：

1. 依存関係を同期してロックファイルを更新：
```bash
uv sync
```

### デバッグ

MCPサーバーはstdioで実行されるため、デバッグが困難な場合があります。最良のデバッグ体験のために、[MCP Inspector](https://github.com/modelcontextprotocol/inspector)の使用を強くお勧めします。

以下のコマンドで`npx`経由でMCP Inspectorを起動できます：

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/py-obsidian-tools run py-obsidian-tools
```

起動すると、Inspectorはブラウザでアクセスしてデバッグを開始できるURLを表示します。

サーバーログを監視したり（設定されている場合）、標準のPythonロギングを使用することもできます。
