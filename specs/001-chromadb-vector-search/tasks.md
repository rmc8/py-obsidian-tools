# Tasks: ChromaDB Vector Search

**Input**: Design documents from `/specs/001-chromadb-vector-search/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/mcp-tools.md, research.md, quickstart.md

**Tests**: Not explicitly requested - test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency configuration

- [ ] T001 Add optional-dependencies [vector] section to pyproject.toml with chromadb>=0.4.0, semantic-text-splitter>=0.18.0
- [ ] T002 Add optional-dependencies [vector-openai], [vector-google], [vector-cohere], [vector-all] sections to pyproject.toml
- [ ] T003 Add pyobsidian-index script entry to pyproject.toml [project.scripts]
- [ ] T004 [P] Create vectorstore module directory structure at src/libs/vectorstore/
- [ ] T005 [P] Create src/libs/vectorstore/__init__.py with module exports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Add VectorConfig class to src/libs/config.py with all embedding provider settings (per data-model.md)
- [ ] T007 Add VectorSearchResult model to src/libs/models.py (per data-model.md)
- [ ] T008 Add IndexStatus model to src/libs/models.py (per data-model.md)
- [ ] T009 Add NoteChunk model to src/libs/models.py (per data-model.md)
- [ ] T010 [P] Add VectorStoreError, IndexNotFoundError, EmbeddingProviderError exceptions to src/libs/exceptions.py
- [ ] T011 Implement BaseEmbeddingProvider abstract class in src/libs/vectorstore/embeddings.py
- [ ] T012 Implement DefaultEmbeddingProvider (all-MiniLM-L6-v2) in src/libs/vectorstore/embeddings.py
- [ ] T013 [P] Implement OllamaEmbeddingProvider in src/libs/vectorstore/embeddings.py
- [ ] T014 [P] Implement OpenAIEmbeddingProvider in src/libs/vectorstore/embeddings.py
- [ ] T015 [P] Implement GoogleEmbeddingProvider in src/libs/vectorstore/embeddings.py
- [ ] T016 [P] Implement CohereEmbeddingProvider in src/libs/vectorstore/embeddings.py
- [ ] T017 Implement embedding provider factory function get_embedding_provider() in src/libs/vectorstore/embeddings.py
- [ ] T018 Implement MarkdownChunker class in src/libs/vectorstore/chunker.py using semantic-text-splitter

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Vault全体のインデックス作成 (Priority: P1) 🎯 MVP

**Goal**: ユーザーがObsidian Vaultの全ノートをベクトルインデックス化し、セマンティック検索の準備をする

**Independent Test**: CLIコマンド `pyobsidian-index full` を実行し、インデックスが作成されることを確認

### Implementation for User Story 1

- [ ] T019 [US1] Implement ObsidianVectorStore class with __init__, _get_collection methods in src/libs/vectorstore/store.py
- [ ] T020 [US1] Implement index_note() method in src/libs/vectorstore/store.py for single note indexing
- [ ] T021 [US1] Implement index_vault() method in src/libs/vectorstore/store.py for full vault indexing
- [ ] T022 [US1] Implement delete_note() method in src/libs/vectorstore/store.py
- [ ] T023 [US1] Implement clear_index() method in src/libs/vectorstore/store.py
- [ ] T024 [US1] Implement get_status() method in src/libs/vectorstore/store.py returning IndexStatus
- [ ] T025 [US1] Implement async wrapper methods using run_in_executor in src/libs/vectorstore/store.py
- [ ] T026 [US1] Create src/indexer.py with argparse CLI structure (full, update, clear, status subcommands)
- [ ] T027 [US1] Implement 'full' subcommand in src/indexer.py calling index_vault()
- [ ] T028 [US1] Implement 'clear' subcommand in src/indexer.py calling clear_index()
- [ ] T029 [US1] Implement 'status' subcommand in src/indexer.py calling get_status()
- [ ] T030 [US1] Add progress display and --verbose flag to src/indexer.py

**Checkpoint**: At this point, User Story 1 should be fully functional - `pyobsidian-index full` creates index

---

## Phase 4: User Story 2 - セマンティック検索 (Priority: P1)

**Goal**: AIエージェントがMCPツール経由で、自然言語クエリでノートを検索する

**Independent Test**: MCPツール `vector_search` を呼び出し、関連ノートが返ることを確認

### Implementation for User Story 2

- [ ] T031 [US2] Implement search() method in src/libs/vectorstore/store.py with query, n_results, folder filter
- [ ] T032 [US2] Add async search wrapper method in src/libs/vectorstore/store.py
- [ ] T033 [US2] Implement vector_search MCP tool in src/main.py (per contracts/mcp-tools.md)
- [ ] T034 [US2] Add error handling for empty index in vector_search tool
- [ ] T035 [US2] Add JSON response formatting for vector_search results

**Checkpoint**: At this point, `vector_search` MCP tool returns semantic search results

---

## Phase 5: User Story 3 - 類似ノート発見 (Priority: P2)

**Goal**: 特定のノートに類似した他のノートを発見する

**Independent Test**: MCPツール `find_similar_notes` を呼び出し、類似ノートが返ることを確認

### Implementation for User Story 3

- [ ] T036 [US3] Implement find_similar() method in src/libs/vectorstore/store.py
- [ ] T037 [US3] Add async find_similar wrapper method in src/libs/vectorstore/store.py
- [ ] T038 [US3] Implement find_similar_notes MCP tool in src/main.py (per contracts/mcp-tools.md)
- [ ] T039 [US3] Add error handling for non-existent note path in find_similar_notes tool
- [ ] T040 [US3] Add JSON response formatting for find_similar_notes results

**Checkpoint**: At this point, `find_similar_notes` MCP tool returns similar notes

---

## Phase 6: User Story 4 - 差分インデックス更新 (Priority: P2)

**Goal**: 新規・変更されたノートのみをインデックス更新する

**Independent Test**: CLIコマンド `pyobsidian-index update` を実行し、変更分のみ更新されることを確認

### Implementation for User Story 4

- [ ] T041 [US4] Implement get_indexed_notes_metadata() method in src/libs/vectorstore/store.py
- [ ] T042 [US4] Implement detect_changes() method in src/libs/vectorstore/store.py (compare mtime)
- [ ] T043 [US4] Implement incremental_update() method in src/libs/vectorstore/store.py
- [ ] T044 [US4] Implement 'update' subcommand in src/indexer.py calling incremental_update()
- [ ] T045 [US4] Add progress display showing new/modified/deleted counts in src/indexer.py

**Checkpoint**: At this point, `pyobsidian-index update` performs differential updates

---

## Phase 7: User Story 5 - 埋め込みプロバイダー選択 (Priority: P3)

**Goal**: ユーザーが埋め込みプロバイダー（ローカル/OpenAI/Google/Cohere/Ollama）を選択できる

**Independent Test**: 環境変数で各プロバイダーを設定し、インデックス作成が成功することを確認

### Implementation for User Story 5

- [ ] T046 [US5] Add provider validation to VectorConfig in src/libs/config.py (require API keys for external providers)
- [ ] T047 [US5] Implement provider switching in ObsidianVectorStore.__init__ based on VectorConfig.provider
- [ ] T048 [US5] Add --provider CLI option to src/indexer.py for runtime provider selection
- [ ] T049 [US5] Implement vector_status MCP tool in src/main.py (per contracts/mcp-tools.md)
- [ ] T050 [US5] Add provider info to get_status() output in src/libs/vectorstore/store.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T051 [P] Update src/libs/vectorstore/__init__.py with final exports
- [ ] T052 [P] Add comprehensive docstrings to all public methods
- [ ] T053 Run ruff check and fix any linting issues
- [ ] T054 Run isort on all source files
- [ ] T055 [P] Update README.md with vector search documentation
- [ ] T056 Run quickstart.md validation manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 are both P1, can run in parallel after Foundational
  - US3, US4, US5 can proceed after or in parallel with US1/US2
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

| Story | Priority | Dependencies | Can Start After |
|-------|----------|--------------|-----------------|
| US1 (Full Index) | P1 | None | Phase 2 |
| US2 (Search) | P1 | US1 (needs index) | Phase 2 + T024 |
| US3 (Similar) | P2 | US1 (needs index) | Phase 2 + T024 |
| US4 (Update) | P2 | US1 (builds on full index) | Phase 3 |
| US5 (Providers) | P3 | None | Phase 2 |

### Within Each User Story

- Core store methods before CLI/MCP tools
- Sync methods before async wrappers
- Implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- T004, T005 (Setup) can run in parallel
- T010, T013-T016 (Embeddings) can run in parallel after T011-T012
- T051, T052, T055 (Polish) can run in parallel
- US2, US3 can start in parallel once index infrastructure (T019-T025) is complete
- US5 can be implemented in parallel with any other user story

---

## Parallel Example: Foundational Phase

```bash
# Launch all embedding providers in parallel (after base class):
Task: "Implement OllamaEmbeddingProvider in src/libs/vectorstore/embeddings.py"
Task: "Implement OpenAIEmbeddingProvider in src/libs/vectorstore/embeddings.py"
Task: "Implement GoogleEmbeddingProvider in src/libs/vectorstore/embeddings.py"
Task: "Implement CohereEmbeddingProvider in src/libs/vectorstore/embeddings.py"
```

## Parallel Example: User Story 2 & 3

```bash
# After T024 (get_status) is complete, both search stories can start:
Task: "[US2] Implement search() method in src/libs/vectorstore/store.py"
Task: "[US3] Implement find_similar() method in src/libs/vectorstore/store.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Full Index)
4. Complete Phase 4: User Story 2 (Search)
5. **STOP and VALIDATE**: Test basic indexing and search independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → `pyobsidian-index full` works → MVP indexing!
3. Add User Story 2 → `vector_search` MCP tool works → MVP search!
4. Add User Story 3 → `find_similar_notes` works → Similar notes feature
5. Add User Story 4 → `pyobsidian-index update` works → Incremental updates
6. Add User Story 5 → Provider selection works → Full flexibility

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- ChromaDB is sync-only; use run_in_executor for async wrappers
