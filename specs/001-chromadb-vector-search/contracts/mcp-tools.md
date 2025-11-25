# MCP Tools Contract: Vector Search

## Overview

PyObsidianMCPに追加するベクトル検索関連のMCPツール定義。

## Tools

### vector_search

セマンティック検索を実行し、クエリに関連するノートを返す。

**Parameters**:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| query | string | Yes | - | 検索クエリ（自然言語） |
| n_results | integer | No | 10 | 返す結果数（1-100） |
| folder | string | No | null | フォルダでフィルタ（例: "Projects"） |

**Returns**: string (JSON formatted)

```json
{
  "results": [
    {
      "path": "Projects/MyProject.md",
      "title": "MyProject",
      "folder": "Projects",
      "score": 0.85,
      "content_preview": "このプロジェクトは...",
      "chunk_index": 0,
      "total_chunks": 3
    }
  ],
  "total": 5,
  "query": "プロジェクト管理について"
}
```

**Errors**:
- `Index not found`: インデックスが存在しない
- `Configuration error`: 設定が不正

**Example**:

```python
@mcp.tool()
async def vector_search(
    query: str,
    n_results: int = 10,
    folder: str | None = None
) -> str:
    """
    Perform semantic search across Obsidian vault.

    Args:
        query: Natural language search query
        n_results: Number of results to return (1-100)
        folder: Optional folder filter (e.g., "Projects")

    Returns:
        JSON string with search results including path, score, and preview
    """
```

---

### find_similar_notes

指定したノートに類似したノートを検索する。

**Parameters**:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| path | string | Yes | - | ノートのパス（例: "Projects/MyProject.md"） |
| n_results | integer | No | 5 | 返す結果数（1-50） |

**Returns**: string (JSON formatted)

```json
{
  "source_note": "Projects/MyProject.md",
  "similar_notes": [
    {
      "path": "Projects/RelatedProject.md",
      "title": "RelatedProject",
      "folder": "Projects",
      "score": 0.78,
      "content_preview": "関連するプロジェクト...",
      "chunk_index": 0,
      "total_chunks": 2
    }
  ],
  "total": 3
}
```

**Errors**:
- `Index not found`: インデックスが存在しない
- `Note not found`: 指定ノートがインデックスにない
- `Configuration error`: 設定が不正

**Example**:

```python
@mcp.tool()
async def find_similar_notes(
    path: str,
    n_results: int = 5
) -> str:
    """
    Find notes similar to a specified note.

    Args:
        path: Path to the source note (e.g., "Projects/MyProject.md")
        n_results: Number of similar notes to return (1-50)

    Returns:
        JSON string with similar notes including path, score, and preview
    """
```

---

### vector_status

インデックスの状態を取得する。

**Parameters**: None

**Returns**: string (JSON formatted)

```json
{
  "status": "ready",
  "collection_name": "obsidian_notes",
  "total_documents": 1523,
  "total_notes": 487,
  "embedding_provider": "default",
  "embedding_dimension": 384,
  "last_updated": "2025-11-25T10:30:00Z",
  "chroma_path": "/Users/user/.obsidian-vector"
}
```

**Status Values**:
- `ready`: インデックスが利用可能
- `empty`: インデックスが空
- `error`: エラー状態

**Errors**:
- `Configuration error`: 設定が不正
- `Database error`: ChromaDBアクセスエラー

**Example**:

```python
@mcp.tool()
async def vector_status() -> str:
    """
    Get the status of the vector search index.

    Returns:
        JSON string with index status including document count,
        embedding provider, and last update time
    """
```

## Error Response Format

すべてのツールは、エラー時に以下の形式で応答する：

```json
{
  "error": true,
  "error_type": "IndexNotFoundError",
  "message": "Vector index not found. Run 'pyobsidian-index full' to create index."
}
```

## CLI Commands Contract

### pyobsidian-index

インデックス管理CLI。

**Subcommands**:

| Command | Description | Options |
|---------|-------------|---------|
| `full` | 全ノートをインデックス | `--verbose`, `--force` |
| `update` | 差分更新 | `--verbose` |
| `clear` | インデックスクリア | `--confirm` |
| `status` | 状態表示 | `--json` |

**Exit Codes**:
- `0`: 成功
- `1`: 一般エラー
- `2`: 設定エラー
- `3`: APIエラー

**Example Output (status)**:

```
Vector Search Index Status
==========================
Collection: obsidian_notes
Documents:  1,523 chunks
Notes:      487 notes
Provider:   default (all-MiniLM-L6-v2)
Dimension:  384
Updated:    2025-11-25 10:30:00
Path:       /Users/user/.obsidian-vector
Status:     Ready
```
