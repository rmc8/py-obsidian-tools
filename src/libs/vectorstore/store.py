"""Vector store implementation using ChromaDB."""

import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import chromadb

from ..config import ObsidianConfig, VectorConfig
from ..exceptions import IndexNotFoundError, VectorStoreError
from ..models import IndexStatus, NoteChunk, VectorSearchResult
from .chunker import MarkdownChunker
from .embeddings import get_embedding_provider


class ObsidianVectorStore:
    """Vector store for Obsidian notes using ChromaDB."""

    def __init__(
        self,
        vector_config: VectorConfig,
        obsidian_config: ObsidianConfig,
    ) -> None:
        """Initialize the vector store.

        Args:
            vector_config: Vector search configuration.
            obsidian_config: Obsidian API configuration.
        """
        self._vector_config = vector_config
        self._obsidian_config = obsidian_config

        # Expand path
        chroma_path = Path(vector_config.chroma_path).expanduser()
        chroma_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB
        self._client = chromadb.PersistentClient(path=str(chroma_path))

        # Initialize embedding provider
        self._embedding_provider = get_embedding_provider(vector_config)

        # Initialize chunker
        self._chunker = MarkdownChunker(chunk_size=vector_config.chunk_size)

        # Thread pool for async wrappers
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._closed = False

    def close(self) -> None:
        """Cleanup resources (ThreadPoolExecutor)."""
        if not self._closed:
            self._executor.shutdown(wait=True)
            self._closed = True

    def __enter__(self) -> "ObsidianVectorStore":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - cleanup resources."""
        self.close()

    async def __aenter__(self) -> "ObsidianVectorStore":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - cleanup resources."""
        self.close()

    def _get_collection(self) -> chromadb.Collection:
        """Get or create the ChromaDB collection."""
        return self._client.get_or_create_collection(
            name=self._vector_config.collection_name,
            embedding_function=self._embedding_provider,
            metadata={"hnsw:space": "cosine"},
        )

    def index_note(
        self,
        path: str,
        content: str,
        mtime: float,
    ) -> int:
        """Index a single note.

        Args:
            path: Note path (e.g., "Projects/MyProject.md").
            content: Note content (markdown).
            mtime: Last modified time (Unix timestamp).

        Returns:
            Number of chunks indexed.
        """
        collection = self._get_collection()

        # Delete existing chunks for this note
        self.delete_note(path)

        # Chunk the content
        chunks = self._chunker.chunk(content)
        if not chunks:
            return 0

        # Prepare data for ChromaDB
        folder = str(Path(path).parent) if "/" in path or "\\" in path else ""
        title = Path(path).stem

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for i, chunk_content in enumerate(chunks):
            chunk_id = f"{path}::{i}"
            ids.append(chunk_id)
            documents.append(chunk_content)
            metadatas.append(
                NoteChunk(
                    path=path,
                    folder=folder,
                    title=title,
                    mtime=mtime,
                    chunk_index=i,
                    total_chunks=len(chunks),
                ).model_dump()
            )

        # Add to collection
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        return len(chunks)

    def _is_external_api_provider(self) -> bool:
        """Check if using external API provider that benefits from parallel processing."""
        return self._vector_config.provider in ("openai", "google", "cohere")

    def _index_note_batch(
        self,
        notes_batch: list[dict],
    ) -> list[dict[str, Any]]:
        """Index a batch of notes in parallel using ThreadPoolExecutor.

        Args:
            notes_batch: List of note dicts with 'path', 'content', 'mtime' keys.

        Returns:
            List of result dicts with 'path', 'chunks', 'error' keys.
        """
        results: list[dict[str, Any]] = []

        def process_note(note: dict) -> dict[str, Any]:
            path = note.get("path", "")
            content = note.get("content", "")
            mtime = note.get("mtime", 0.0)
            try:
                chunks = self.index_note(path, content, mtime)
                return {"path": path, "chunks": chunks, "error": None}
            except Exception as e:
                return {"path": path, "chunks": 0, "error": str(e)}

        batch_size = self._vector_config.batch_size
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            results = list(executor.map(process_note, notes_batch))

        return results

    def index_vault(
        self,
        notes: list[dict],
        progress_callback: Callable | None = None,
    ) -> dict:
        """Index all notes in the vault.

        Args:
            notes: List of note dicts with 'path', 'content', 'mtime' keys.
            progress_callback: Optional callback(current, total, path) for progress.

        Returns:
            Dict with 'total_notes', 'total_chunks', 'errors' keys.
        """
        total_notes = 0
        total_chunks = 0
        errors: list[dict] = []

        # Use parallel processing for external API providers
        if self._is_external_api_provider():
            batch_size = self._vector_config.batch_size
            processed = 0

            for i in range(0, len(notes), batch_size):
                batch = notes[i : i + batch_size]
                results = self._index_note_batch(batch)

                for result in results:
                    processed += 1
                    if result["error"]:
                        errors.append(
                            {"path": result["path"], "error": result["error"]}
                        )
                    else:
                        total_notes += 1
                        total_chunks += result["chunks"]

                    if progress_callback:
                        progress_callback(processed, len(notes), result["path"])
        else:
            # Sequential processing for local providers
            for i, note in enumerate(notes):
                path = note.get("path", "")
                content = note.get("content", "")
                mtime = note.get("mtime", 0.0)

                try:
                    chunks = self.index_note(path, content, mtime)
                    total_notes += 1
                    total_chunks += chunks

                    if progress_callback:
                        progress_callback(i + 1, len(notes), path)
                except Exception as e:
                    errors.append({"path": path, "error": str(e)})

        return {
            "total_notes": total_notes,
            "total_chunks": total_chunks,
            "errors": errors,
        }

    def delete_note(self, path: str) -> int:
        """Delete all chunks for a note.

        Args:
            path: Note path.

        Returns:
            Number of chunks deleted.
        """
        collection = self._get_collection()

        # Find all chunks for this note
        results = collection.get(
            where={"path": path},
            include=[],
        )

        if results["ids"]:
            collection.delete(ids=results["ids"])
            return len(results["ids"])
        return 0

    def clear_index(self) -> None:
        """Clear the entire index."""
        try:
            self._client.delete_collection(self._vector_config.collection_name)
        except Exception:
            pass  # Collection might not exist

    def get_status(self) -> IndexStatus:
        """Get the index status.

        Returns:
            IndexStatus with collection info.
        """
        try:
            collection = self._get_collection()
            count = collection.count()

            # Get unique note count
            all_metadata = collection.get(include=["metadatas"])
            unique_paths = set()
            last_mtime: float | None = None

            for meta in all_metadata.get("metadatas", []):
                if meta:
                    unique_paths.add(meta.get("path", ""))
                    mtime = meta.get("mtime", 0)
                    if last_mtime is None or mtime > last_mtime:
                        last_mtime = mtime

            last_updated = None
            if last_mtime:
                last_updated = datetime.fromtimestamp(last_mtime, tz=timezone.utc)

            return IndexStatus(
                collection_name=self._vector_config.collection_name,
                total_documents=count,
                total_notes=len(unique_paths),
                embedding_provider=self._embedding_provider.name(),
                embedding_dimension=self._embedding_provider.dimension(),
                last_updated=last_updated,
                chroma_path=str(Path(self._vector_config.chroma_path).expanduser()),
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to get status: {e}") from e

    def search(
        self,
        query: str,
        n_results: int = 10,
        folder: str | None = None,
    ) -> list[VectorSearchResult]:
        """Search for notes matching the query.

        Args:
            query: Natural language search query.
            n_results: Number of results to return (1-100).
            folder: Optional folder filter.

        Returns:
            List of search results.
        """
        collection = self._get_collection()

        if collection.count() == 0:
            raise IndexNotFoundError(
                "Vector index is empty. Run 'pyobsidian-index full' to create index."
            )

        # Build where filter
        where = None
        if folder:
            where = {"folder": folder}

        # Query
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, 100),
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        # Convert to VectorSearchResult
        search_results: list[VectorSearchResult] = []

        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                document = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i] if results["distances"] else 1.0

                # Convert distance to similarity score (cosine distance to similarity)
                score = max(0.0, min(1.0, 1.0 - distance))

                # Create preview (max 200 chars)
                preview = document[:200] if document else ""

                search_results.append(
                    VectorSearchResult(
                        path=metadata.get("path", ""),
                        title=metadata.get("title", ""),
                        folder=metadata.get("folder", ""),
                        score=round(score, 4),
                        content_preview=preview,
                        chunk_index=metadata.get("chunk_index", 0),
                        total_chunks=metadata.get("total_chunks", 1),
                    )
                )

        return search_results

    def find_similar(
        self,
        path: str,
        n_results: int = 5,
    ) -> list[VectorSearchResult]:
        """Find notes similar to the given note.

        Args:
            path: Path to the source note.
            n_results: Number of results to return (1-50).

        Returns:
            List of similar notes (excluding the source note).
        """
        collection = self._get_collection()

        if collection.count() == 0:
            raise IndexNotFoundError(
                "Vector index is empty. Run 'pyobsidian-index full' to create index."
            )

        # Get the first chunk of the source note
        source_chunks = collection.get(
            where={"$and": [{"path": path}, {"chunk_index": 0}]},
            include=["documents", "embeddings"],
        )

        if not source_chunks["ids"]:
            raise IndexNotFoundError(f"Note not found in index: {path}")

        # Use the embedding of the first chunk to find similar
        source_embedding = source_chunks["embeddings"][0]

        # Query for similar, excluding the source note
        results = collection.query(
            query_embeddings=[source_embedding],
            n_results=min(n_results + 10, 60),  # Get extra to filter out source
            include=["documents", "metadatas", "distances"],
        )

        # Convert to VectorSearchResult, filtering out the source note
        search_results: list[VectorSearchResult] = []
        seen_paths: set[str] = set()

        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                result_path = metadata.get("path", "")

                # Skip source note and duplicates
                if result_path == path or result_path in seen_paths:
                    continue

                seen_paths.add(result_path)
                document = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i] if results["distances"] else 1.0

                score = max(0.0, min(1.0, 1.0 - distance))
                preview = document[:200] if document else ""

                search_results.append(
                    VectorSearchResult(
                        path=result_path,
                        title=metadata.get("title", ""),
                        folder=metadata.get("folder", ""),
                        score=round(score, 4),
                        content_preview=preview,
                        chunk_index=metadata.get("chunk_index", 0),
                        total_chunks=metadata.get("total_chunks", 1),
                    )
                )

                if len(search_results) >= n_results:
                    break

        return search_results

    def get_indexed_notes_metadata(self) -> dict[str, float]:
        """Get metadata for all indexed notes.

        Returns:
            Dict mapping path to mtime.
        """
        collection = self._get_collection()
        all_metadata = collection.get(
            where={"chunk_index": 0},
            include=["metadatas"],
        )

        result: dict[str, float] = {}
        for meta in all_metadata.get("metadatas", []):
            if meta:
                result[meta.get("path", "")] = meta.get("mtime", 0.0)
        return result

    def detect_changes(
        self,
        current_notes: list[dict],
    ) -> dict:
        """Detect changes between current notes and indexed notes.

        Args:
            current_notes: List of note dicts with 'path', 'mtime' keys.

        Returns:
            Dict with 'new', 'modified', 'deleted' lists of paths.
        """
        indexed = self.get_indexed_notes_metadata()
        current_paths = {note["path"]: note["mtime"] for note in current_notes}

        new_notes: list[str] = []
        modified_notes: list[str] = []
        deleted_notes: list[str] = []

        # Find new and modified
        for path, mtime in current_paths.items():
            if path not in indexed:
                new_notes.append(path)
            elif mtime > indexed[path]:
                modified_notes.append(path)

        # Find deleted
        for path in indexed:
            if path not in current_paths:
                deleted_notes.append(path)

        return {
            "new": new_notes,
            "modified": modified_notes,
            "deleted": deleted_notes,
        }

    def incremental_update(
        self,
        notes_to_add: list[dict],
        notes_to_delete: list[str],
        progress_callback: Callable | None = None,
    ) -> dict:
        """Perform incremental update of the index.

        Args:
            notes_to_add: Notes to add/update (with 'path', 'content', 'mtime').
            notes_to_delete: Paths of notes to delete.
            progress_callback: Optional callback(current, total, path).

        Returns:
            Dict with update statistics.
        """
        deleted_count = 0
        added_count = 0
        chunks_count = 0
        errors: list[dict] = []

        total = len(notes_to_delete) + len(notes_to_add)
        current = 0

        # Delete removed notes
        for path in notes_to_delete:
            try:
                self.delete_note(path)
                deleted_count += 1
                current += 1
                if progress_callback:
                    progress_callback(current, total, f"Deleted: {path}")
            except Exception as e:
                errors.append({"path": path, "error": str(e)})

        # Add/update notes - use parallel processing for external API providers
        if self._is_external_api_provider() and notes_to_add:
            batch_size = self._vector_config.batch_size

            for i in range(0, len(notes_to_add), batch_size):
                batch = notes_to_add[i : i + batch_size]
                results = self._index_note_batch(batch)

                for result in results:
                    current += 1
                    if result["error"]:
                        errors.append(
                            {"path": result["path"], "error": result["error"]}
                        )
                    else:
                        added_count += 1
                        chunks_count += result["chunks"]

                    if progress_callback:
                        progress_callback(current, total, result["path"])
        else:
            # Sequential processing for local providers
            for note in notes_to_add:
                path = note.get("path", "")
                content = note.get("content", "")
                mtime = note.get("mtime", 0.0)

                try:
                    chunks = self.index_note(path, content, mtime)
                    added_count += 1
                    chunks_count += chunks
                    current += 1
                    if progress_callback:
                        progress_callback(current, total, path)
                except Exception as e:
                    errors.append({"path": path, "error": str(e)})

        return {
            "added": added_count,
            "deleted": deleted_count,
            "chunks": chunks_count,
            "errors": errors,
        }

    # Async wrapper methods using run_in_executor

    async def async_index_note(
        self,
        path: str,
        content: str,
        mtime: float,
    ) -> int:
        """Async wrapper for index_note."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self.index_note,
            path,
            content,
            mtime,
        )

    async def async_index_vault(
        self,
        notes: list[dict],
        progress_callback: Callable | None = None,
    ) -> dict:
        """Async wrapper for index_vault."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self.index_vault,
            notes,
            progress_callback,
        )

    async def async_delete_note(self, path: str) -> int:
        """Async wrapper for delete_note."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self.delete_note,
            path,
        )

    async def async_clear_index(self) -> None:
        """Async wrapper for clear_index."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            self.clear_index,
        )

    async def async_get_status(self) -> IndexStatus:
        """Async wrapper for get_status."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self.get_status,
        )

    async def async_search(
        self,
        query: str,
        n_results: int = 10,
        folder: str | None = None,
    ) -> list[VectorSearchResult]:
        """Async wrapper for search."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self.search,
            query,
            n_results,
            folder,
        )

    async def async_find_similar(
        self,
        path: str,
        n_results: int = 5,
    ) -> list[VectorSearchResult]:
        """Async wrapper for find_similar."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self.find_similar,
            path,
            n_results,
        )
