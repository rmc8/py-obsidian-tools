# Quickstart: ChromaDB Vector Search

## Prerequisites

- Python 3.13+
- Obsidian with [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin installed and running
- (Optional) Ollama for local high-quality embeddings
- (Optional) API keys for OpenAI/Google/Cohere

## Installation

### Basic (Local Embeddings)

```bash
# uvxで直接実行（インストール不要）
uvx pyobsidianmcp

# または、vectorオプション付きでインストール
pip install "pyobsidianmcp[vector]"
```

### With External Embedding Providers

```bash
# OpenAI埋め込み
pip install "pyobsidianmcp[vector-openai]"

# Google埋め込み
pip install "pyobsidianmcp[vector-google]"

# Cohere埋め込み
pip install "pyobsidianmcp[vector-cohere]"

# 全プロバイダー
pip install "pyobsidianmcp[vector-all]"
```

## Configuration

### Environment Variables

```bash
# 必須: Obsidian REST API設定
export OBSIDIAN_API_KEY=your-api-key
export OBSIDIAN_HOST=127.0.0.1
export OBSIDIAN_PORT=27123

# オプション: Vector Search設定
export VECTOR_CHROMA_PATH=~/.obsidian-vector
export VECTOR_COLLECTION_NAME=obsidian_notes
export VECTOR_CHUNK_SIZE=512

# 埋め込みプロバイダー選択（default|ollama|openai|google|cohere）
export VECTOR_PROVIDER=default

# Ollama使用時
export VECTOR_OLLAMA_HOST=http://localhost:11434
export VECTOR_OLLAMA_MODEL=nomic-embed-text

# OpenAI使用時
export VECTOR_OPENAI_API_KEY=sk-xxx
export VECTOR_OPENAI_MODEL=text-embedding-3-small

# Google使用時
export VECTOR_GOOGLE_API_KEY=xxx
export VECTOR_GOOGLE_MODEL=embedding-001

# Cohere使用時
export VECTOR_COHERE_API_KEY=xxx
export VECTOR_COHERE_MODEL=embed-multilingual-v3.0
```

### .env File

```bash
# .env
OBSIDIAN_API_KEY=your-api-key
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123

VECTOR_PROVIDER=default
VECTOR_CHROMA_PATH=~/.obsidian-vector
```

## Usage

### Step 1: Create Index

```bash
# 全ノートをインデックス（初回）
pyobsidian-index full

# 進捗表示
pyobsidian-index full --verbose
```

### Step 2: Use with Claude Desktop

Claude Desktop設定（`claude_desktop_config.json`）:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["pyobsidianmcp"],
      "env": {
        "OBSIDIAN_API_KEY": "your-api-key",
        "VECTOR_PROVIDER": "default"
      }
    }
  }
}
```

### Step 3: Search

MCPツールを使用:

```
# セマンティック検索
vector_search("プロジェクト管理について")

# フォルダフィルタ付き
vector_search("会議メモ", folder="Work")

# 類似ノート検索
find_similar_notes("Projects/MyProject.md")

# インデックス状態確認
vector_status()
```

## CLI Commands

```bash
# 全ノートをインデックス
pyobsidian-index full

# 差分更新（変更分のみ）
pyobsidian-index update

# インデックスクリア
pyobsidian-index clear

# 状態確認
pyobsidian-index status
```

## Embedding Provider Selection

| Provider | Command | Best For |
|----------|---------|----------|
| default | `VECTOR_PROVIDER=default` | 高速、無料、ローカル完結 |
| ollama | `VECTOR_PROVIDER=ollama` | ローカルで高品質 |
| openai | `VECTOR_PROVIDER=openai` | 最高品質、多言語 |
| google | `VECTOR_PROVIDER=google` | Google AI連携 |
| cohere | `VECTOR_PROVIDER=cohere` | 多言語特化 |

### Example: Using OpenAI Embeddings

```bash
export VECTOR_PROVIDER=openai
export VECTOR_OPENAI_API_KEY=sk-xxx
export VECTOR_OPENAI_MODEL=text-embedding-3-small

pyobsidian-index full
```

### Example: Using Ollama Embeddings

```bash
# 1. Ollamaでモデルをダウンロード
ollama pull nomic-embed-text

# 2. 環境変数設定
export VECTOR_PROVIDER=ollama
export VECTOR_OLLAMA_HOST=http://localhost:11434
export VECTOR_OLLAMA_MODEL=nomic-embed-text

# 3. インデックス作成
pyobsidian-index full
```

## Troubleshooting

### Index Creation Fails

```bash
# Obsidian REST APIが稼働中か確認
curl http://localhost:27123/vault/ -H "Authorization: Bearer YOUR_API_KEY"

# ChromaDBパスの権限確認
ls -la ~/.obsidian-vector
```

### Search Returns No Results

```bash
# インデックス状態確認
pyobsidian-index status

# インデックスが空の場合は再作成
pyobsidian-index full
```

### OpenAI API Error

```bash
# APIキーが有効か確認
echo $VECTOR_OPENAI_API_KEY

# デフォルト埋め込みにフォールバック
export VECTOR_PROVIDER=default
```
