"""CLI for managing Obsidian vector search index."""

import argparse
import asyncio
import json
import sys

from .libs.client import ObsidianClient
from .libs.config import load_config, load_vector_config
from .libs.exceptions import (IndexNotFoundError, ObsidianAPIError,
                              VectorConfigError, VectorStoreError)
from .libs.vectorstore.store import ObsidianVectorStore


def print_progress(current: int, total: int, path: str, verbose: bool = False) -> None:
    """Print progress indicator."""
    percent = (current / total) * 100 if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * current / total) if total > 0 else 0
    bar = "=" * filled + "-" * (bar_len - filled)

    if verbose:
        print(f"\r[{bar}] {percent:5.1f}% ({current}/{total}) {path[:50]:<50}", end="")
    else:
        print(f"\r[{bar}] {percent:5.1f}% ({current}/{total})", end="")

    if current >= total:
        print()


async def fetch_all_notes(
    client: ObsidianClient,
    verbose: bool = False,
) -> list[dict]:
    """Fetch all notes from Obsidian vault."""
    files = await client.list_files()
    md_files = [f for f in files if f.endswith(".md")]

    notes: list[dict] = []
    for i, path in enumerate(md_files):
        try:
            note = await client.get_note(path)
            mtime = 0.0
            if note.stat and "mtime" in note.stat:
                mtime = note.stat["mtime"] / 1000  # Convert ms to seconds

            notes.append(
                {
                    "path": path,
                    "content": note.content,
                    "mtime": mtime,
                }
            )

            if verbose and (i + 1) % 10 == 0:
                print(f"  Fetched {i + 1}/{len(md_files)} notes...")
        except Exception as e:
            if verbose:
                print(f"  Warning: Failed to fetch {path}: {e}")

    return notes


async def cmd_full(args: argparse.Namespace) -> int:
    """Execute full indexing command."""
    try:
        obsidian_config = load_config()
        obsidian_config.validate_config()
        vector_config = load_vector_config()
    except (VectorConfigError, Exception) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 2

    print("Obsidian Vector Search Indexer")
    print("=" * 40)
    print(f"Provider: {vector_config.provider}")
    print(f"ChromaDB path: {vector_config.chroma_path}")
    print()

    try:
        # Clear existing index if --force
        store = ObsidianVectorStore(vector_config, obsidian_config)
        if args.force:
            print("Clearing existing index...")
            store.clear_index()

        # Fetch notes
        print("Fetching notes from Obsidian...")
        async with ObsidianClient(obsidian_config) as client:
            notes = await fetch_all_notes(client, args.verbose)

        if not notes:
            print("No notes found in vault.")
            return 0

        print(f"Found {len(notes)} notes.")
        print("Indexing...")

        # Index
        def progress(current: int, total: int, path: str) -> None:
            print_progress(current, total, path, args.verbose)

        result = store.index_vault(notes, progress_callback=progress)

        print()
        print("Indexing complete!")
        print(f"  Notes indexed: {result['total_notes']}")
        print(f"  Chunks created: {result['total_chunks']}")
        if result["errors"]:
            print(f"  Errors: {len(result['errors'])}")
            if args.verbose:
                for err in result["errors"]:
                    print(f"    - {err['path']}: {err['error']}")

        return 0

    except ObsidianAPIError as e:
        print(f"Obsidian API error: {e}", file=sys.stderr)
        return 3
    except VectorStoreError as e:
        print(f"Vector store error: {e}", file=sys.stderr)
        return 1


async def cmd_update(args: argparse.Namespace) -> int:
    """Execute incremental update command."""
    try:
        obsidian_config = load_config()
        obsidian_config.validate_config()
        vector_config = load_vector_config()
    except (VectorConfigError, Exception) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 2

    print("Obsidian Vector Search - Incremental Update")
    print("=" * 40)

    try:
        store = ObsidianVectorStore(vector_config, obsidian_config)

        # Fetch current notes metadata
        print("Fetching notes from Obsidian...")
        async with ObsidianClient(obsidian_config) as client:
            files = await client.list_files()
            md_files = [f for f in files if f.endswith(".md")]

            current_notes: list[dict] = []
            for path in md_files:
                try:
                    note = await client.get_note(path)
                    mtime = 0.0
                    if note.stat and "mtime" in note.stat:
                        mtime = note.stat["mtime"] / 1000
                    current_notes.append(
                        {"path": path, "mtime": mtime, "content": note.content}
                    )
                except Exception:
                    pass

        # Detect changes
        print("Detecting changes...")
        changes = store.detect_changes(current_notes)

        new_count = len(changes["new"])
        mod_count = len(changes["modified"])
        del_count = len(changes["deleted"])

        print(f"  New: {new_count}")
        print(f"  Modified: {mod_count}")
        print(f"  Deleted: {del_count}")

        if new_count == 0 and mod_count == 0 and del_count == 0:
            print("No changes detected.")
            return 0

        # Prepare notes to update
        notes_to_add = [
            n
            for n in current_notes
            if n["path"] in changes["new"] or n["path"] in changes["modified"]
        ]

        # Update
        print("Updating index...")

        def progress(current: int, total: int, path: str) -> None:
            print_progress(current, total, path, args.verbose)

        result = store.incremental_update(
            notes_to_add=notes_to_add,
            notes_to_delete=changes["deleted"],
            progress_callback=progress,
        )

        print()
        print("Update complete!")
        print(f"  Added/Updated: {result['added']}")
        print(f"  Deleted: {result['deleted']}")
        print(f"  Chunks: {result['chunks']}")
        if result["errors"]:
            print(f"  Errors: {len(result['errors'])}")

        return 0

    except ObsidianAPIError as e:
        print(f"Obsidian API error: {e}", file=sys.stderr)
        return 3
    except VectorStoreError as e:
        print(f"Vector store error: {e}", file=sys.stderr)
        return 1


async def cmd_clear(args: argparse.Namespace) -> int:
    """Execute clear index command."""
    try:
        vector_config = load_vector_config()
        obsidian_config = load_config()
    except (VectorConfigError, Exception) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 2

    if not args.confirm:
        print("This will delete the entire vector index.")
        response = input("Are you sure? (y/N): ")
        if response.lower() != "y":
            print("Cancelled.")
            return 0

    try:
        store = ObsidianVectorStore(vector_config, obsidian_config)
        store.clear_index()
        print("Index cleared successfully.")
        return 0
    except VectorStoreError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


async def cmd_status(args: argparse.Namespace) -> int:
    """Execute status command."""
    try:
        vector_config = load_vector_config()
        obsidian_config = load_config()
    except (VectorConfigError, Exception) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 2

    try:
        store = ObsidianVectorStore(vector_config, obsidian_config)
        status = store.get_status()

        if args.json:
            print(json.dumps(status.model_dump(), default=str, indent=2))
        else:
            print("Vector Search Index Status")
            print("=" * 40)
            print(f"Collection: {status.collection_name}")
            print(f"Documents:  {status.total_documents:,} chunks")
            print(f"Notes:      {status.total_notes:,} notes")
            print(f"Provider:   {status.embedding_provider}")
            print(f"Dimension:  {status.embedding_dimension}")
            if status.last_updated:
                print(
                    f"Updated:    {status.last_updated.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            else:
                print("Updated:    Never")
            print(f"Path:       {status.chroma_path}")

            if status.total_documents > 0:
                print("Status:     Ready")
            else:
                print("Status:     Empty")

        return 0

    except IndexNotFoundError:
        if args.json:
            print(json.dumps({"status": "empty", "error": "Index not found"}))
        else:
            print("Index not found. Run 'pyobsidian-index full' to create index.")
        return 0
    except VectorStoreError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="pyobsidian-index",
        description="Manage Obsidian vector search index",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # full subcommand
    full_parser = subparsers.add_parser("full", help="Create full index of all notes")
    full_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed progress"
    )
    full_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Clear existing index before indexing",
    )

    # update subcommand
    update_parser = subparsers.add_parser(
        "update", help="Incremental update (new/modified only)"
    )
    update_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed progress"
    )

    # clear subcommand
    clear_parser = subparsers.add_parser("clear", help="Clear the index")
    clear_parser.add_argument(
        "--confirm", "-y", action="store_true", help="Skip confirmation prompt"
    )

    # status subcommand
    status_parser = subparsers.add_parser("status", help="Show index status")
    status_parser.add_argument(
        "--json", "-j", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()

    # Run the appropriate command
    if args.command == "full":
        exit_code = asyncio.run(cmd_full(args))
    elif args.command == "update":
        exit_code = asyncio.run(cmd_update(args))
    elif args.command == "clear":
        exit_code = asyncio.run(cmd_clear(args))
    elif args.command == "status":
        exit_code = asyncio.run(cmd_status(args))
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
