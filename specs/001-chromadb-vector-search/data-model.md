# Data Model: ChromaDB Vector Search

## Entities

### VectorConfig

設定管理用Pydanticモデル。

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class VectorConfig(BaseSettings):
    """ベクトル検索の設定"""
    model_config = SettingsConfigDict(env_prefix="VECTOR_")

    # ChromaDB設定
    chroma_path: str = ".chroma"
    collection_name: str = "obsidian_notes"

    # チャンキング設定
    chunk_size: int = 512

    # 埋め込みプロバイダー設定
    provider: Literal["default", "ollama", "openai", "google", "cohere"] = "default"

    # Ollama設定
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "nomic-embed-text"

    # OpenAI設定
    openai_api_key: str | None = None
    openai_model: str = "text-embedding-3-small"

    # Google設定
    google_api_key: str | None = None
    google_model: str = "embedding-001"

    # Cohere設定
    cohere_api_key: str | None = None
    cohere_model: str = "embed-multilingual-v3.0"
```

### NoteChunk

ChromaDBに保存されるチャンクのメタデータスキーマ。

```python
from pydantic import BaseModel

class NoteChunk(BaseModel):
    """ノートチャンクのメタデータ"""
    path: str           # ノートのパス（例: "Projects/MyProject.md"）
    folder: str         # 親フォルダ（例: "Projects"）
    title: str          # ノートタイトル（例: "MyProject"）
    mtime: float        # 最終更新日時（Unix timestamp）
    chunk_index: int    # チャンク番号（0-indexed）
    total_chunks: int   # ノートの総チャンク数
```

**ChromaDB Storage**:
```python
# ChromaDBへの保存形式
collection.add(
    ids=["Projects/MyProject.md::0", "Projects/MyProject.md::1"],
    documents=["チャンク1の内容...", "チャンク2の内容..."],
    metadatas=[
        {
            "path": "Projects/MyProject.md",
            "folder": "Projects",
            "title": "MyProject",
            "mtime": 1700000000.0,
            "chunk_index": 0,
            "total_chunks": 2
        },
        {
            "path": "Projects/MyProject.md",
            "folder": "Projects",
            "title": "MyProject",
            "mtime": 1700000000.0,
            "chunk_index": 1,
            "total_chunks": 2
        }
    ]
)
```

### VectorSearchResult

検索結果のPydanticモデル。

```python
from pydantic import BaseModel

class VectorSearchResult(BaseModel):
    """ベクトル検索の結果"""
    path: str              # ノートのパス
    title: str             # ノートタイトル
    folder: str            # 親フォルダ
    score: float           # 類似度スコア（0-1、高いほど類似）
    content_preview: str   # チャンク内容のプレビュー（最大200文字）
    chunk_index: int       # チャンク番号
    total_chunks: int      # ノートの総チャンク数
```

### IndexStatus

インデックス状態のPydanticモデル。

```python
from pydantic import BaseModel
from datetime import datetime

class IndexStatus(BaseModel):
    """インデックスの状態"""
    collection_name: str        # コレクション名
    total_documents: int        # 総ドキュメント数（チャンク数）
    total_notes: int            # 総ノート数
    embedding_provider: str     # 使用中の埋め込みプロバイダー
    embedding_dimension: int    # 埋め込み次元数
    last_updated: datetime | None  # 最終更新日時
    chroma_path: str            # ChromaDBのパス
```

## Relationships

```
┌──────────────┐     1:N      ┌──────────────┐
│ ObsidianNote │ ──────────── │  NoteChunk   │
│              │              │              │
│ path (PK)    │              │ id (PK)      │
│ content      │              │ path (FK)    │
│ mtime        │              │ chunk_index  │
└──────────────┘              │ content      │
                              │ embedding    │
                              └──────────────┘
                                    │
                                    │ N:1
                                    ▼
                              ┌──────────────┐
                              │  ChromaDB    │
                              │  Collection  │
                              │              │
                              │ name         │
                              │ metadata     │
                              └──────────────┘
```

## Validation Rules

### VectorConfig
- `chunk_size`: 100 ≤ value ≤ 4000
- `provider`: enum値のみ許可
- `openai_api_key`: provider="openai"の場合は必須
- `google_api_key`: provider="google"の場合は必須
- `cohere_api_key`: provider="cohere"の場合は必須

### NoteChunk
- `path`: 空文字不可、`.md`拡張子推奨
- `chunk_index`: 0以上の整数
- `total_chunks`: 1以上の整数、chunk_index < total_chunks

### VectorSearchResult
- `score`: 0.0 ≤ value ≤ 1.0
- `content_preview`: 最大200文字

## State Transitions

### Index Lifecycle

```
                    ┌─────────────┐
                    │   Empty     │
                    └──────┬──────┘
                           │ pyobsidian-index full
                           ▼
                    ┌─────────────┐
         update ──▶ │  Indexed    │ ◀── full (rebuild)
                    └──────┬──────┘
                           │ pyobsidian-index clear
                           ▼
                    ┌─────────────┐
                    │   Empty     │
                    └─────────────┘
```

### Note Update Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    pyobsidian-index update                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ Get all notes from API │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ Compare with ChromaDB  │
              └───────────┬────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │   New    │   │ Modified │   │ Deleted  │
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         │              │              │
         ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │   Add    │   │  Update  │   │  Delete  │
    │ to index │   │  index   │   │ from idx │
    └──────────┘   └──────────┘   └──────────┘
```

## Embedding Provider Interface

```python
from abc import ABC, abstractmethod
from chromadb import EmbeddingFunction

class BaseEmbeddingProvider(EmbeddingFunction, ABC):
    """埋め込みプロバイダーの基底クラス"""

    @abstractmethod
    def __call__(self, input: list[str]) -> list[list[float]]:
        """テキストを埋め込みベクトルに変換"""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """埋め込み次元数を返す"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """プロバイダー名を返す"""
        pass
```

### Provider Implementations

| Provider | Class | Dimension |
|----------|-------|-----------|
| default | DefaultEmbeddingProvider | 384 |
| ollama | OllamaEmbeddingProvider | 768 |
| openai | OpenAIEmbeddingProvider | 1536 |
| google | GoogleEmbeddingProvider | 768 |
| cohere | CohereEmbeddingProvider | 1024 |
