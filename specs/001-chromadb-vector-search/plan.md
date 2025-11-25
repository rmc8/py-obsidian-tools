# Implementation Plan: ChromaDB Vector Search

**Branch**: `001-chromadb-vector-search` | **Date**: 2025-11-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-chromadb-vector-search/spec.md`

## Summary

ObsidianノートのセマンティックベクトルインデックスをChromaDBで実現する。Markdownチャンキングにsemantic-text-splitter、埋め込みにChromaDB内蔵機能（all-MiniLM-L6-v2）をデフォルトとし、オプションでOpenAI/Google/Cohere/Ollamaを選択可能にする。

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: chromadb, semantic-text-splitter, httpx, pydantic, mcp
**Optional Dependencies**: openai (OpenAI埋め込み), google-generativeai (Google埋め込み), cohere (Cohere埋め込み)
**Storage**: ChromaDB PersistentClient（ローカルSQLite + Parquet）
**Testing**: pytest（既存プロジェクトに合わせる）
**Target Platform**: macOS/Linux/Windows（UVXで実行可能）
**Project Type**: Single project（既存構造を拡張）
**Performance Goals**: 1000ノート/10分インデックス、検索1秒以内
**Constraints**: デフォルトは外部APIコール不要、オプションで外部API使用可
**Scale/Scope**: 数千〜数万ノートのVault対応

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 状態 | 詳細 |
|------|------|------|
| I. MCP優先設計 | ✅ PASS | 全機能はMCPツールとして実装。stdio transport使用。 |
| II. UVX互換性 | ✅ PASS | optional-dependenciesで分離。uvxで実行可能。 |
| III. Pydanticによる型安全性 | ✅ PASS | VectorConfig, VectorSearchResult等をPydanticで定義。 |
| IV. 非同期優先アーキテクチャ | ⚠️ PARTIAL | ChromaDBは同期API。run_in_executorでラップ。 |
| V. シンプルさと最小依存関係 | ✅ PASS | 必須依存は2つ（chromadb, semantic-text-splitter）のみ。 |

**注記**: ChromaDBは同期APIのため、asyncio.run_in_executorでラップして非同期コンテキストと統合する。

## Project Structure

### Documentation (this feature)

```text
specs/001-chromadb-vector-search/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (MCP tool definitions)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── main.py              # MCPサーバー（ベクトル検索ツール追加）
├── indexer.py           # 新規: インデックスCLI
└── libs/
    ├── client.py        # 既存: Obsidian REST APIクライアント
    ├── config.py        # 拡張: VectorConfig追加
    ├── models.py        # 拡張: VectorSearchResult追加
    ├── exceptions.py    # 既存: カスタム例外
    └── vectorstore/     # 新規: ベクトルストアモジュール
        ├── __init__.py  # エクスポート
        ├── store.py     # ObsidianVectorStore
        ├── chunker.py   # MarkdownChunker
        └── embeddings.py # 埋め込みプロバイダー

tests/
└── test_vectorstore.py  # ベクトルストアテスト
```

**Structure Decision**: 既存のsrc/libs/構造を拡張し、vectorstore/サブモジュールを追加。

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| embeddings.py追加 | 複数プロバイダー対応 | 単一プロバイダーではユーザーの選択肢が制限される |
| run_in_executor使用 | ChromaDB同期API | ChromaDBに非同期APIがない |

## Embedding Providers

| Provider | Model | Dimensions | Local | API Key Required |
|----------|-------|------------|-------|------------------|
| default | all-MiniLM-L6-v2 | 384 | ✅ | ❌ |
| ollama | nomic-embed-text | 768 | ✅ | ❌ |
| openai | text-embedding-3-small | 1536 | ❌ | ✅ |
| google | embedding-001 | 768 | ❌ | ✅ |
| cohere | embed-multilingual-v3.0 | 1024 | ❌ | ✅ |

**デフォルト**: `default`（all-MiniLM-L6-v2、ローカル実行、外部APIコール不要）

## Environment Variables

```bash
# Obsidian REST API（既存）
OBSIDIAN_API_KEY=xxx
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123

# Vector Search（新規）
VECTOR_CHROMA_PATH=~/.obsidian-vector
VECTOR_COLLECTION_NAME=obsidian_notes
VECTOR_CHUNK_SIZE=512
VECTOR_PROVIDER=default         # default | ollama | openai | google | cohere
VECTOR_OLLAMA_HOST=http://localhost:11434
VECTOR_OLLAMA_MODEL=nomic-embed-text
VECTOR_OPENAI_API_KEY=sk-xxx
VECTOR_OPENAI_MODEL=text-embedding-3-small
VECTOR_GOOGLE_API_KEY=xxx
VECTOR_GOOGLE_MODEL=embedding-001
VECTOR_COHERE_API_KEY=xxx
VECTOR_COHERE_MODEL=embed-multilingual-v3.0
```

## Implementation Phases

### Phase 1: Core Infrastructure
1. pyproject.toml に optional-dependencies 追加
2. VectorConfig 追加（config.py）
3. embeddings.py 実装（プロバイダー抽象化 + 全プロバイダー実装）

### Phase 2: Vector Store
4. chunker.py 実装（MarkdownChunker）
5. store.py 実装（ObsidianVectorStore）

### Phase 3: CLI & MCP Tools
6. indexer.py CLI実装
7. MCPツール追加（main.py）

### Phase 4: Quality
8. テスト実装
9. ドキュメント更新

## MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `vector_search` | セマンティック検索 | query, n_results, folder_filter |
| `find_similar_notes` | 類似ノート検索 | path, n_results |
| `vector_status` | インデックス状態 | (none) |

## CLI Commands

```bash
pyobsidian-index full      # 全ノートインデックス
pyobsidian-index update    # 差分更新
pyobsidian-index clear     # インデックスクリア
pyobsidian-index status    # 状態表示
```
