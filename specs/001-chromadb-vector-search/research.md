# Research: ChromaDB Vector Search

## Decision Log

### 1. Vector Database Selection

**Decision**: ChromaDB

**Rationale**:
- PythonネイティブでMCPサーバーとの統合が容易
- PersistentClientでローカルファイルベースの永続化が可能
- 内蔵埋め込み関数（DefaultEmbeddingFunction）でローカル完結可能
- 外部プロバイダー（OpenAI、Google、Cohere、Ollama）も公式サポート
- Apache 2.0ライセンスでオープンソース

**Alternatives considered**:
- **Qdrant**: 高性能だがPython統合がChromaDBほど自然ではない
- **Pinecone**: クラウドベースでローカル完結の要件に合わない
- **FAISS**: 低レベルAPIで開発コストが高い
- **LanceDB**: 新しく実績が少ない

### 2. Embedding Provider Strategy

**Decision**: デフォルトはall-MiniLM-L6-v2（ローカル）、オプションで外部APIプロバイダー

**Rationale**:
- **設計制約の例外**: 埋め込み（ベクトル化）のためだけに外部APIの使用を許可
- デフォルトはローカル完結で外部依存なし
- ユーザーが品質向上を望む場合は外部プロバイダーを選択可能
- 各プロバイダーは`optional-dependencies`で分離

**Provider Details**:

| Provider | Model | Dimensions | Use Case |
|----------|-------|------------|----------|
| default | all-MiniLM-L6-v2 | 384 | ローカル完結、高速、無料 |
| ollama | nomic-embed-text | 768 | ローカルLLM、高品質 |
| openai | text-embedding-3-small | 1536 | 最高品質、多言語対応 |
| google | embedding-001 | 768 | Google AI連携 |
| cohere | embed-multilingual-v3.0 | 1024 | 多言語特化 |

### 3. Text Chunking Strategy

**Decision**: semantic-text-splitter (MarkdownSplitter)

**Rationale**:
- Rust製で高速（LangChainの87%高速という報告あり）
- Markdown構造（見出し、段落、コードブロック）を認識
- LangChain依存なしの純粋な分割ライブラリ
- セマンティック境界で分割し、意味の断片化を防ぐ

**Configuration**:
- chunk_size: 512文字（デフォルト）
- 環境変数`VECTOR_CHUNK_SIZE`で調整可能

**Alternatives considered**:
- **LangChain RecursiveCharacterTextSplitter**: 制約によりLangChain不可
- **semchunk**: 純粋Python、Markdown特化機能が弱い
- **カスタム実装**: 開発コストが高い

### 4. Async Integration Pattern

**Decision**: asyncio.run_in_executor でChromaDB同期APIをラップ

**Rationale**:
- ChromaDBは同期APIのみ提供
- MCPサーバーは非同期コンテキストで動作
- run_in_executorでブロッキング操作を別スレッドで実行

**Implementation**:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ObsidianVectorStore:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=2)

    async def search(self, query: str, n_results: int = 10):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._sync_search,
            query,
            n_results
        )

    def _sync_search(self, query: str, n_results: int):
        # ChromaDB同期API呼び出し
        return self.collection.query(query_texts=[query], n_results=n_results)
```

### 5. Metadata Schema

**Decision**: 以下のメタデータフィールドを保存

| Field | Type | Purpose |
|-------|------|---------|
| path | string | ノートのパス（一意識別子） |
| folder | string | 親フォルダ（フィルタリング用） |
| title | string | ノートタイトル |
| mtime | float | 最終更新日時（差分更新用） |
| chunk_index | int | チャンク番号（同一ノート内） |
| total_chunks | int | ノートの総チャンク数 |

**Rationale**:
- `path`と`chunk_index`の組み合わせで各チャンクを一意に識別
- `folder`でフォルダベースのフィルタリングが可能
- `mtime`で差分更新を効率化

### 6. Index Update Strategy

**Decision**: 手動更新（フル + 差分）

**Rationale**:
- 自動監視はMCPサーバーの責務外
- CLIで明示的に更新をトリガー
- 差分更新でパフォーマンス最適化

**Diff Detection Logic**:
1. Obsidian REST APIから全ファイル一覧取得
2. 各ファイルのmtimeを取得
3. ChromaDBに保存済みのmtimeと比較
4. 新規・更新・削除を検出して処理

### 7. Error Handling Strategy

**Decision**: 階層的例外クラス + グレースフルデグラデーション

**Exceptions**:
```python
class VectorStoreError(Exception):
    """ベクトルストア操作の基底例外"""

class IndexNotFoundError(VectorStoreError):
    """インデックスが存在しない"""

class EmbeddingProviderError(VectorStoreError):
    """埋め込みプロバイダーエラー"""

class ChunkingError(VectorStoreError):
    """チャンキングエラー"""
```

**Graceful Degradation**:
- 外部API失敗時はローカル埋め込みにフォールバック（設定可能）
- 部分インデックス失敗時は成功分を保持

## Technical Constraints Clarification

### 制約の明確化

1. **LangChain不使用**: ✅ semantic-text-splitterで対応
2. **外部AI APIコールの制限**: ⚠️ **例外あり**
   - 埋め込み（ベクトル化）のためだけにOpenAI/Google/Cohereの使用を許可
   - それ以外の生成AI機能（チャット、要約等）は不可
3. **ローカル完結がデフォルト**: ✅ all-MiniLM-L6-v2がデフォルト

## Dependencies

### Required (vector feature)
```toml
[project.optional-dependencies]
vector = [
    "chromadb>=0.4.0",
    "semantic-text-splitter>=0.18.0",
]
```

### Optional (embedding providers)
```toml
[project.optional-dependencies]
vector-openai = [
    "pyobsidianmcp[vector]",
    "openai>=1.0.0",
]
vector-google = [
    "pyobsidianmcp[vector]",
    "google-generativeai>=0.3.0",
]
vector-cohere = [
    "pyobsidianmcp[vector]",
    "cohere>=5.0.0",
]
vector-all = [
    "pyobsidianmcp[vector-openai]",
    "pyobsidianmcp[vector-google]",
    "pyobsidianmcp[vector-cohere]",
]
```

## Performance Considerations

### Indexing Performance
- バッチ処理: 100ノート単位でChromaDBにadd
- 並列チャンキング: ThreadPoolExecutorで並列処理
- 目標: 1000ノート/10分（デフォルト埋め込み）

### Search Performance
- ChromaDB HNSWインデックス: O(log n)検索
- 目標: 1秒以内のレスポンス

### Memory Usage
- チャンクサイズ512文字で、1000ノートあたり約50MB
- PersistentClientでディスクベース永続化
