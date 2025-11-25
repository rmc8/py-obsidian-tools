🌐 **Language / 言語**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/PyObsidianMCP?style=flat)](https://github.com/rmc8/PyObsidianMCP/commits)

# PyObsidianMCP

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
| `get_recent_periodic_notes` | 最近の定期ノートを取得 |
| `open_note` | ObsidianのUIでノートを開く |
| `get_active_note` | 現在アクティブなノートを取得 |
| `update_active_note` | アクティブなノートの内容を更新 |
| `append_active_note` | アクティブなノートにコンテンツを追加 |

### プロンプト例

まずClaudeにObsidianを使うように指示すると良いでしょう。そうすれば常にツールを呼び出します。

以下のようなプロンプトを使用できます：
- 「'Daily'フォルダ内のすべてのノートをリストして」
- 「'プロジェクトX'に言及しているすべてのノートを検索して要約して」
- 「私たちの議論の内容で'会議メモ'という新しいノートを作成して」
- 「デイリーノートに'TODO: PRをレビュー'を追記して」
- 「アクティブなノートの内容を取得して批評して」
- 「complex searchを使用してWorkフォルダ内のすべてのmarkdownファイルを検索して」

## 設定

### Obsidian REST APIキー

Obsidian REST APIキーで環境を設定する方法は2つあります。

1. サーバー設定に追加（推奨）

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

2. 作業ディレクトリに以下の必須変数を含む`.env`ファイルを作成：

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123
```

注意：
- APIキーはObsidianのプラグイン設定（設定 > Local REST API > セキュリティ）で確認できます
- デフォルトポートは27123です
- デフォルトホストは127.0.0.1（localhost）です

## クイックスタート

### インストール

#### Obsidian REST API

Obsidian REST APIコミュニティプラグインが実行されている必要があります：https://github.com/coddingtonbear/obsidian-local-rest-api

設定でインストールして有効にし、APIキーをコピーしてください。

#### Claude Desktop

MacOSの場合：`~/Library/Application\ Support/Claude/claude_desktop_config.json`

Windowsの場合：`%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>開発/未公開サーバー設定</summary>

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
  <summary>GitHubからインストール（uvx）</summary>

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
npx @modelcontextprotocol/inspector uv --directory /path/to/pyobsidianmcp run pyobsidianmcp
```

起動すると、Inspectorはブラウザでアクセスしてデバッグを開始できるURLを表示します。

サーバーログを監視したり（設定されている場合）、標準のPythonロギングを使用することもできます。
