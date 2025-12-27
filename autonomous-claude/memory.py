#!/usr/bin/env python3
"""
Memory interface for Autonomous Claude.
Handles both short-term (SQLite) and long-term (Qdrant) memory.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid

SHORT_TERM_DB = "/autonomous-claude/data/memory/short_term.db"
LONG_TERM_COLLECTION = "claude_memory"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333


class ShortTermMemory:
    """SQLite-based short-term memory (last 50 entries)."""

    def __init__(self, db_path: str = SHORT_TERM_DB):
        self.db_path = db_path

    def add(self, memory_type: str, content: str) -> int:
        """Add a memory entry. Returns the entry ID."""
        if memory_type not in ['action', 'observation', 'thought', 'goal']:
            raise ValueError(f"Invalid memory type: {memory_type}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO memories (timestamp, type, content)
            VALUES (?, ?, ?)
        """, (datetime.utcnow().isoformat(), memory_type, content))

        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return memory_id

    def get_recent(self, limit: int = 50) -> List[Dict]:
        """Retrieve recent memories (up to limit, default 50)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, type, content
            FROM memories
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        memories = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Return in chronological order (oldest first)
        return list(reversed(memories))

    def get_by_type(self, memory_type: str, limit: int = 10) -> List[Dict]:
        """Get recent memories of a specific type."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, type, content
            FROM memories
            WHERE type = ?
            ORDER BY id DESC
            LIMIT ?
        """, (memory_type, limit))

        memories = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return list(reversed(memories))

    def clear(self) -> None:
        """Clear all memories (use with caution)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories")
        conn.commit()
        conn.close()


class LongTermMemory:
    """Qdrant-based long-term memory with semantic search."""

    def __init__(self, host: str = QDRANT_HOST, port: int = QDRANT_PORT):
        self.host = host
        self.port = port
        self.collection = LONG_TERM_COLLECTION
        self.qdrant_available = False

        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, PointStruct
            self.client = QdrantClient(host=host, port=port)
            self.qdrant_available = True
            self._ensure_collection()
        except ImportError:
            print("⚠ qdrant-client not installed. Long-term memory disabled.")
            print("  Install with: pip install qdrant-client")
        except Exception as e:
            print(f"⚠ Qdrant not available: {e}")
            print("  Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        if not self.qdrant_available:
            return

        try:
            from qdrant_client.models import Distance, VectorParams
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection for c in collections)

            if not exists:
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"✓ Created Qdrant collection: {self.collection}")
        except Exception as e:
            print(f"⚠ Error creating collection: {e}")
            self.qdrant_available = False

    def add(self, content: str, memory_type: str, tags: List[str] = None,
            importance: int = 5) -> Optional[str]:
        """
        Store a memory in long-term storage.

        Args:
            content: The memory content
            memory_type: One of: fact, skill, preference, lesson, discovery
            tags: Optional list of tags
            importance: 1-10 scale, higher = more important

        Returns:
            UUID of stored memory, or None if failed
        """
        if not self.qdrant_available:
            return None

        if memory_type not in ['fact', 'skill', 'preference', 'lesson', 'discovery']:
            raise ValueError(f"Invalid memory type: {memory_type}")

        if importance < 1 or importance > 10:
            raise ValueError(f"Importance must be 1-10, got {importance}")

        try:
            from qdrant_client.models import PointStruct
            from sentence_transformers import SentenceTransformer

            # Generate embedding (using a lightweight model)
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(content).tolist()

            # Create point
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": memory_type,
                    "tags": tags or [],
                    "content": content,
                    "importance": importance
                }
            )

            self.client.upsert(
                collection_name=self.collection,
                points=[point]
            )

            return point_id
        except Exception as e:
            print(f"⚠ Error storing long-term memory: {e}")
            return None

    def search(self, query: str, limit: int = 5,
               min_importance: int = 1) -> List[Dict]:
        """
        Semantic search for relevant memories.

        Args:
            query: Search query
            limit: Maximum results
            min_importance: Only return memories with importance >= this

        Returns:
            List of matching memories with scores
        """
        if not self.qdrant_available:
            return []

        try:
            from sentence_transformers import SentenceTransformer

            # Generate query embedding
            model = SentenceTransformer('all-MiniLM-L6-v2')
            query_embedding = model.encode(query).tolist()

            # Search
            results = self.client.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                limit=limit,
                query_filter={
                    "must": [
                        {
                            "key": "importance",
                            "range": {"gte": min_importance}
                        }
                    ]
                }
            )

            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    **hit.payload
                }
                for hit in results
            ]
        except Exception as e:
            print(f"⚠ Error searching long-term memory: {e}")
            return []


# Global instances
short_term = ShortTermMemory()
long_term = LongTermMemory()


if __name__ == "__main__":
    # Test short-term memory
    print("Testing short-term memory...")
    short_term.add("thought", "Testing the memory system")
    recent = short_term.get_recent(10)
    print(f"Recent memories: {len(recent)}")
    for m in recent:
        print(f"  [{m['type']}] {m['content']}")

    # Test long-term memory
    if long_term.qdrant_available:
        print("\nTesting long-term memory...")
        long_term.add(
            "Python is installed at /usr/local/bin/python3",
            memory_type="fact",
            tags=["python", "environment"],
            importance=7
        )
        results = long_term.search("where is python", limit=3)
        print(f"Search results: {len(results)}")
        for r in results:
            print(f"  [{r['type']}] {r['content']} (score: {r['score']:.3f})")
    else:
        print("\nLong-term memory not available (Qdrant not running)")
