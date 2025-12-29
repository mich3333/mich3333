#!/usr/bin/env python3
"""
Initialize the Autonomous Claude memory system.
Sets up SQLite short-term memory database.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = "/autonomous-claude/data/memory/short_term.db"

def setup_short_term_memory():
    """Create SQLite database with schema for short-term memory."""

    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create memories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('action', 'observation', 'thought', 'goal')),
            content TEXT NOT NULL
        )
    """)

    # Create indexes for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp DESC)
    """)

    # Index on type for get_by_type queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_type_id ON memories(type, id DESC)
    """)

    # Create trigger to maintain last 50 entries
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS maintain_recent_memories
        AFTER INSERT ON memories
        BEGIN
            DELETE FROM memories
            WHERE id NOT IN (
                SELECT id FROM memories
                ORDER BY id DESC
                LIMIT 50
            );
        END
    """)

    conn.commit()

    # Insert initial setup record
    cursor.execute("""
        INSERT INTO memories (timestamp, type, content)
        VALUES (?, 'action', 'Memory system initialized and database created')
    """, (datetime.utcnow().isoformat(),))

    conn.commit()
    conn.close()

    print(f"✓ Short-term memory database created at {DB_PATH}")
    return True

if __name__ == "__main__":
    setup_short_term_memory()
