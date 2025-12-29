"""
Unit Tests for Autonomous Claude Memory System
"""
import pytest
import os
import sys
import sqlite3
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from memory import ShortTermMemory, LongTermMemory


def init_test_db(db_path):
    """Initialize test database with schema."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('action', 'observation', 'thought', 'goal')),
            content TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp DESC)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_type_id ON memories(type, id DESC)
    """)

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
    conn.close()


class TestShortTermMemory:
    """Test suite for ShortTermMemory."""

    @pytest.fixture
    def memory(self, tmp_path):
        """Create a temporary memory instance with initialized database."""
        db_path = tmp_path / "test_memory.db"
        init_test_db(db_path)
        return ShortTermMemory(db_path=str(db_path))

    def test_add_memory(self, memory):
        """Test adding a memory."""
        memory_id = memory.add('thought', 'Test thought')
        assert memory_id > 0
        assert isinstance(memory_id, int)

    def test_add_different_types(self, memory):
        """Test adding different memory types."""
        types = ['goal', 'thought', 'action', 'observation']
        for mem_type in types:
            memory_id = memory.add(mem_type, f'Test {mem_type}')
            assert memory_id > 0

    def test_invalid_memory_type(self, memory):
        """Test adding invalid memory type raises error."""
        with pytest.raises(ValueError):
            memory.add('invalid_type', 'Test content')

    def test_get_recent(self, memory):
        """Test retrieving recent memories."""
        # Add some memories
        for i in range(10):
            memory.add('thought', f'Thought {i}')

        recent = memory.get_recent(5)
        assert len(recent) == 5
        assert recent[0]['content'] == 'Thought 9'  # Most recent first

    def test_get_by_type(self, memory):
        """Test retrieving memories by type."""
        # Add different types
        memory.add('goal', 'Goal 1')
        memory.add('thought', 'Thought 1')
        memory.add('action', 'Action 1')

        goals = memory.get_by_type('goal')
        assert len(goals) == 1
        assert goals[0]['type'] == 'goal'

    def test_memory_cleanup_trigger(self, memory):
        """Test that auto-cleanup trigger works."""
        # Add more than 50 memories
        for i in range(60):
            memory.add('thought', f'Thought {i}')

        # Should keep only last 50
        all_memories = memory.get_recent(100)
        assert len(all_memories) == 50

    def test_timestamp_format(self, memory):
        """Test that timestamps are properly formatted."""
        memory_id = memory.add('thought', 'Test')
        recent = memory.get_recent(1)

        assert 'timestamp' in recent[0]
        # Should be able to parse as datetime
        timestamp = recent[0]['timestamp']
        assert isinstance(timestamp, (str, datetime))


class TestLongTermMemory:
    """Test suite for LongTermMemory."""

    @pytest.fixture
    def ltm(self):
        """Create a long-term memory instance."""
        return LongTermMemory()

    def test_add_memory(self, ltm):
        """Test adding to long-term memory."""
        # Should not crash even if Qdrant not available
        ltm.add('Test knowledge', 'observation', tags=['test'])

    def test_query_memory(self, ltm):
        """Test querying long-term memory."""
        # Should return empty list if Qdrant not available
        results = ltm.search('test query')
        assert isinstance(results, list)

    def test_graceful_degradation(self, ltm):
        """Test that system works without Qdrant."""
        # Should not raise errors
        ltm.add('Test', 'thought')
        results = ltm.search('Test')
        assert results == []  # Empty if Qdrant unavailable


class TestMemoryIntegration:
    """Integration tests for memory system."""

    def test_memory_workflow(self, tmp_path):
        """Test complete memory workflow."""
        # Create memory
        db_path = tmp_path / "workflow_test.db"
        init_test_db(db_path)
        stm = ShortTermMemory(db_path=str(db_path))

        # Add a goal
        goal_id = stm.add('goal', 'Test goal')
        assert goal_id > 0

        # Add thoughts
        stm.add('thought', 'Thinking about the goal')
        stm.add('thought', 'Analyzing options')

        # Add action
        stm.add('action', 'Taking action')

        # Add observation
        stm.add('observation', 'Observed result')

        # Verify we can retrieve the workflow
        recent = stm.get_recent(10)
        assert len(recent) == 5

        # Verify order (newest first)
        assert recent[0]['type'] == 'observation'
        assert recent[-1]['type'] == 'goal'

    def test_concurrent_access(self, tmp_path):
        """Test multiple memory instances."""
        db_path = tmp_path / "concurrent_test.db"
        init_test_db(db_path)

        mem1 = ShortTermMemory(db_path=str(db_path))
        mem2 = ShortTermMemory(db_path=str(db_path))

        mem1.add('thought', 'From instance 1')
        mem2.add('thought', 'From instance 2')

        # Both should see both memories
        memories1 = mem1.get_recent(10)
        memories2 = mem2.get_recent(10)

        assert len(memories1) == 2
        assert len(memories2) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
