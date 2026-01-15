#!/usr/bin/env python3
"""
Test script to verify memory system setup.
"""
import sys

def test_imports():
    """Test if all required packages are installed."""
    print("Testing imports...")

    try:
        import sqlite3
        print("  ✓ sqlite3 (built-in)")
    except ImportError as e:
        print(f"  ✗ sqlite3: {e}")
        return False

    try:
        import qdrant_client
        print(f"  ✓ qdrant-client")
    except ImportError as e:
        print(f"  ✗ qdrant-client: {e}")
        return False

    try:
        import sentence_transformers
        print(f"  ✓ sentence-transformers")
    except ImportError as e:
        print(f"  ✗ sentence-transformers: {e}")
        return False

    return True

def test_short_term_memory():
    """Test short-term memory (SQLite)."""
    print("\nTesting short-term memory...")

    try:
        from memory import short_term

        # Add a test memory
        memory_id = short_term.add("thought", "Testing the memory system setup")
        print(f"  ✓ Added memory with ID: {memory_id}")

        # Retrieve recent memories
        recent = short_term.get_recent(5)
        print(f"  ✓ Retrieved {len(recent)} recent memories")

        # Get by type
        thoughts = short_term.get_by_type("thought", 5)
        print(f"  ✓ Retrieved {len(thoughts)} thoughts")

        return True
    except Exception as e:
        print(f"  ✗ Short-term memory test failed: {e}")
        return False

def test_long_term_memory():
    """Test long-term memory (Qdrant)."""
    print("\nTesting long-term memory...")

    try:
        from memory import long_term

        if not long_term.qdrant_available:
            print("  ⚠ Qdrant not available (expected - server not running)")
            print("  ℹ To enable: docker run -p 6333:6333 qdrant/qdrant")
            return True

        # Add a test memory
        memory_id = long_term.add(
            content="Python is a programming language",
            memory_type="fact",
            tags=["python", "programming"],
            importance=8
        )
        print(f"  ✓ Added long-term memory with ID: {memory_id}")

        # Search
        results = long_term.search("What is Python?", limit=3)
        print(f"  ✓ Search returned {len(results)} results")

        return True
    except Exception as e:
        print(f"  ✗ Long-term memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_analytics():
    """Test memory analytics."""
    print("\nTesting memory analytics...")

    try:
        from memory_analytics import stats, health_monitor, pattern_detector, insight_generator

        # Get overview
        overview = stats.get_overview()
        print(f"  ✓ Overview: {overview['total_memories']} total memories")

        # Get health score
        health = health_monitor.get_health_score()
        print(f"  ✓ Health score: {health['score']}/100 ({health['status']})")

        # Detect patterns
        patterns = pattern_detector.detect_patterns()
        print(f"  ✓ Pattern detection completed")

        # Generate insights
        insights_data = insight_generator.generate_insights()
        print(f"  ✓ Generated {insights_data['summary']['total_insights']} insights")

        return True
    except Exception as e:
        print(f"  ✗ Analytics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Memory System Setup Test")
    print("=" * 60)

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test short-term memory
    results.append(("Short-term memory", test_short_term_memory()))

    # Test long-term memory
    results.append(("Long-term memory", test_long_term_memory()))

    # Test analytics
    results.append(("Memory analytics", test_memory_analytics()))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {name}: {status}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
