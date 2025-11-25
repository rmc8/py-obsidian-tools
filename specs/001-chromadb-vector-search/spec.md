# Feature Specification: ChromaDB Vector Search

**Feature Branch**: `001-chromadb-vector-search`
**Created**: 2025-11-25
**Status**: Draft
**Input**: ChromaDBでのインデックス検索機能を追加。ローカル埋め込み（all-MiniLM-L6-v2）をデフォルトとし、オプションでOpenAI・Google・Cohere・Ollamaも選択可能。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Vault全体のインデックス作成 (Priority: P1)

ユーザーがObsidian Vaultの全ノートをベクトルインデックス化し、セマンティック検索の準備をする。

**Why this priority**: セマンティック検索の基盤となる機能。これがないと他の機能が動作しない。

**Independent Test**: CLIコマンド `pyobsidian-index full` を実行し、インデックスが作成されることを確認。

**Acceptance Scenarios**:

1. **Given** ObsidianのLocal REST APIが稼働中, **When** `pyobsidian-index full`を実行, **Then** 全ノートがChromaDBにインデックスされる
2. **Given** インデックスが既に存在, **When** `pyobsidian-index full`を再実行, **Then** インデックスが再構築される
3. **Given** Vault内に1000ノート, **When** `pyobsidian-index full`を実行, **Then** 全ノートが5分以内にインデックスされる

---

### User Story 2 - セマンティック検索 (Priority: P1)

AIエージェントがMCPツール経由で、自然言語クエリでノートを検索する。

**Why this priority**: コア機能。ユーザー価値の中心。

**Independent Test**: MCPツール `vector_search` を呼び出し、関連ノートが返ることを確認。

**Acceptance Scenarios**:

1. **Given** インデックス済みVault, **When** `vector_search("プロジェクト管理について")`を呼び出し, **Then** 関連度順にノート一覧が返る
2. **Given** インデックス済みVault, **When** フォルダフィルタ付きで検索, **Then** 指定フォルダ内のノートのみ返る
3. **Given** 空のインデックス, **When** 検索実行, **Then** 適切なエラーメッセージが返る

---

### User Story 3 - 類似ノート発見 (Priority: P2)

特定のノートに類似した他のノートを発見する。

**Why this priority**: ナレッジ発見の補助機能。

**Independent Test**: MCPツール `find_similar_notes` を呼び出し、類似ノートが返ることを確認。

**Acceptance Scenarios**:

1. **Given** インデックス済みVault, **When** `find_similar_notes("Projects/MyProject.md")`を呼び出し, **Then** 類似度順にノート一覧が返る
2. **Given** 存在しないノートパス, **When** 検索実行, **Then** 適切なエラーメッセージが返る

---

### User Story 4 - 差分インデックス更新 (Priority: P2)

新規・変更されたノートのみをインデックス更新する。

**Why this priority**: 大規模Vaultでの効率的な運用に必要。

**Independent Test**: CLIコマンド `pyobsidian-index update` を実行し、変更分のみ更新されることを確認。

**Acceptance Scenarios**:

1. **Given** インデックス済みVault + 新規ノート追加, **When** `pyobsidian-index update`を実行, **Then** 新規ノートのみインデックスに追加
2. **Given** インデックス済みVault + 既存ノート編集, **When** `pyobsidian-index update`を実行, **Then** 変更ノートのみ再インデックス
3. **Given** インデックス済みVault + ノート削除, **When** `pyobsidian-index update`を実行, **Then** 削除ノートがインデックスから除去

---

### User Story 5 - 埋め込みプロバイダー選択 (Priority: P3)

ユーザーが埋め込みプロバイダー（ローカル/OpenAI/Google/Cohere/Ollama）を選択できる。

**Why this priority**: 柔軟性と品質向上オプション。デフォルト（ローカル）で動作するため優先度低め。

**Independent Test**: 環境変数で各プロバイダーを設定し、インデックス作成が成功することを確認。

**Acceptance Scenarios**:

1. **Given** `VECTOR_PROVIDER=default`, **When** インデックス作成, **Then** all-MiniLM-L6-v2で埋め込み生成
2. **Given** `VECTOR_PROVIDER=openai` + 有効なAPIキー, **When** インデックス作成, **Then** OpenAI text-embedding-3-smallで埋め込み生成
3. **Given** `VECTOR_PROVIDER=openai` + 無効なAPIキー, **When** インデックス作成, **Then** 適切なエラーメッセージ

---

### Edge Cases

- インデックス作成中にObsidian REST APIが停止した場合はどうなるか？ → 部分インデックスを保持し、再開可能にする
- 非常に大きなノート（100KB以上）の場合はどうなるか？ → チャンク分割で対応
- バイナリファイル（画像、PDF）がVaultにある場合は？ → Markdownファイルのみ処理
- 日本語・中国語などマルチバイト文字の場合は？ → UTF-8で正常処理

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムはObsidian Vault全体をChromaDBにインデックス化できなければならない
- **FR-002**: システムはMarkdownファイルを意味単位でチャンク分割しなければならない
- **FR-003**: システムは自然言語クエリでセマンティック検索を提供しなければならない
- **FR-004**: システムは類似ノート検索を提供しなければならない
- **FR-005**: システムは差分インデックス更新をサポートしなければならない
- **FR-006**: システムはフォルダによるフィルタリングをサポートしなければならない
- **FR-007**: システムはインデックス状態を確認できなければならない
- **FR-008**: システムは複数の埋め込みプロバイダーをサポートしなければならない
  - デフォルト: all-MiniLM-L6-v2（ローカル、ONNX）
  - OpenAI: text-embedding-3-small
  - Google: embedding-001
  - Cohere: embed-multilingual-v3.0
  - Ollama: nomic-embed-text（ローカル）

### Key Entities

- **VectorIndex**: ChromaDBコレクション。ノートチャンクの埋め込みを保存
- **NoteChunk**: 分割されたノートの断片。path, content, chunk_index, metadataを持つ
- **SearchResult**: 検索結果。path, score, content_preview, metadataを持つ
- **EmbeddingProvider**: 埋め込み生成プロバイダーの抽象化

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 1000ノートのVaultを10分以内にインデックス化できる（デフォルト埋め込み使用時）
- **SC-002**: セマンティック検索が1秒以内に結果を返す
- **SC-003**: 類似ノート検索が1秒以内に結果を返す
- **SC-004**: 差分更新が変更ノート数 × 0.5秒以内に完了する
- **SC-005**: ChromaDBインデックスサイズが元のVaultサイズの2倍以下
