#!/usr/bin/env python3
"""
Autonomous Claude Decision Loop Framework.

This implements the core decision-making cycle:
1. READ short-term memory (context)
2. QUERY long-term memory (relevant past learnings)
3. THINK about what to do next
4. ACT - execute decision
5. RECORD - write to short-term memory
6. OPTIONALLY - store significant learnings to long-term memory
"""
import sys
import json
from datetime import datetime
from typing import Optional, Dict, List
from memory import short_term, long_term


class DecisionLoop:
    """Core autonomous decision-making loop."""

    def __init__(self):
        self.context = {
            "goals": [],
            "current_task": None,
            "iteration": 0
        }

    def read_context(self) -> Dict:
        """Step 1: Read recent short-term memories to understand context."""
        print("\n=== READING CONTEXT ===")

        recent_memories = short_term.get_recent(limit=50)

        # Organize by type
        context = {
            "recent_actions": [m for m in recent_memories if m['type'] == 'action'],
            "recent_observations": [m for m in recent_memories if m['type'] == 'observation'],
            "recent_thoughts": [m for m in recent_memories if m['type'] == 'thought'],
            "active_goals": [m for m in recent_memories if m['type'] == 'goal'],
        }

        print(f"  Recent actions: {len(context['recent_actions'])}")
        print(f"  Recent observations: {len(context['recent_observations'])}")
        print(f"  Recent thoughts: {len(context['recent_thoughts'])}")
        print(f"  Active goals: {len(context['active_goals'])}")

        # Show last 5 entries
        if recent_memories:
            print("\n  Last 5 memories:")
            for m in recent_memories[-5:]:
                print(f"    [{m['type']}] {m['content'][:80]}")

        return context

    def query_knowledge(self, query: str) -> List[Dict]:
        """Step 2: Query long-term memory for relevant past learnings."""
        print(f"\n=== QUERYING KNOWLEDGE ===")
        print(f"  Query: {query}")

        if not long_term.qdrant_available:
            print("  ⚠ Long-term memory not available")
            return []

        results = long_term.search(query, limit=5, min_importance=5)

        if results:
            print(f"  Found {len(results)} relevant memories:")
            for r in results:
                print(f"    [{r['type']}] {r['content'][:80]} (score: {r['score']:.3f})")
        else:
            print("  No relevant memories found")

        return results

    def think(self, context: Dict, knowledge: List[Dict], situation: str) -> str:
        """Step 3: Think about what to do next."""
        print(f"\n=== THINKING ===")
        print(f"  Situation: {situation}")

        # This is where Claude's reasoning happens
        # In practice, this would involve the AI model making a decision

        thought = f"Analyzing situation: {situation}"
        print(f"  Thought: {thought}")

        return thought

    def act(self, action_description: str, action_func=None) -> Dict:
        """Step 4: Execute an action."""
        print(f"\n=== ACTING ===")
        print(f"  Action: {action_description}")

        result = {
            "action": action_description,
            "timestamp": datetime.utcnow().isoformat(),
            "success": True,
            "output": None
        }

        if action_func:
            try:
                output = action_func()
                result["output"] = output
                print(f"  ✓ Action completed successfully")
            except Exception as e:
                result["success"] = False
                result["output"] = str(e)
                print(f"  ✗ Action failed: {e}")

        return result

    def record(self, memory_type: str, content: str) -> int:
        """Step 5: Record to short-term memory."""
        print(f"\n=== RECORDING ===")
        print(f"  Type: {memory_type}")
        print(f"  Content: {content[:80]}...")

        memory_id = short_term.add(memory_type, content)
        print(f"  ✓ Recorded as memory #{memory_id}")

        return memory_id

    def save_learning(self, content: str, memory_type: str,
                     importance: int = 5, tags: List[str] = None) -> Optional[str]:
        """Step 6 (optional): Save significant learning to long-term memory."""
        print(f"\n=== SAVING LEARNING ===")
        print(f"  Type: {memory_type}")
        print(f"  Importance: {importance}/10")
        print(f"  Content: {content[:80]}...")

        if not long_term.qdrant_available:
            print("  ⚠ Long-term memory not available, skipping")
            return None

        memory_id = long_term.add(content, memory_type, tags, importance)

        if memory_id:
            print(f"  ✓ Saved to long-term memory: {memory_id}")
        else:
            print(f"  ✗ Failed to save to long-term memory")

        return memory_id

    def run_cycle(self, situation: str, task_query: Optional[str] = None):
        """Run one complete decision cycle."""
        self.context["iteration"] += 1

        print(f"\n{'='*60}")
        print(f"DECISION CYCLE #{self.context['iteration']}")
        print(f"{'='*60}")

        # 1. Read context
        context = self.read_context()

        # 2. Query knowledge (if relevant)
        knowledge = []
        if task_query:
            knowledge = self.query_knowledge(task_query)

        # 3. Think
        thought = self.think(context, knowledge, situation)
        self.record("thought", thought)

        # 4. Act (placeholder - in real use, this would be actual actions)
        action_result = self.act(f"Considering: {situation}")
        self.record("action", action_result["action"])

        # 5. Observe result
        observation = f"Action {'succeeded' if action_result['success'] else 'failed'}"
        self.record("observation", observation)

        print(f"\n{'='*60}")
        print(f"CYCLE #{self.context['iteration']} COMPLETE")
        print(f"{'='*60}\n")


def demo_decision_loop():
    """Demonstrate the decision loop."""
    loop = DecisionLoop()

    # Set a goal
    short_term.add("goal", "Set up autonomous Claude memory system")

    # Run a decision cycle
    loop.run_cycle(
        situation="Memory system initialized, need to create decision framework",
        task_query="decision loop patterns"
    )

    # Example of saving a significant learning
    loop.save_learning(
        content="The decision loop should read context, query knowledge, think, act, and record",
        memory_type="lesson",
        importance=8,
        tags=["decision-loop", "architecture", "autonomous"]
    )


if __name__ == "__main__":
    demo_decision_loop()
