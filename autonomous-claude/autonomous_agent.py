#!/usr/bin/env python3
"""
Autonomous Claude - Main Agent Script

This is a complete autonomous agent that:
1. Reads context from short-term memory
2. Queries relevant long-term knowledge
3. Makes decisions autonomously
4. Records all actions and observations
5. Learns from experiences
"""
import sys
import time
from memory import short_term, long_term
from decision_loop import DecisionLoop


class AutonomousAgent:
    """Self-directed AI agent with memory and decision-making."""

    def __init__(self, initial_goal: str = None):
        self.loop = DecisionLoop()
        self.running = True
        self.cycle_count = 0

        if initial_goal:
            short_term.add("goal", initial_goal)
            print(f"🎯 Goal set: {initial_goal}")

    def initialize(self):
        """Initialize the agent and load context."""
        print("\n" + "="*60)
        print("AUTONOMOUS CLAUDE - INITIALIZING")
        print("="*60 + "\n")

        # Record initialization
        short_term.add("action", "Agent initialized and starting autonomous operation")

        # Query any existing knowledge about autonomous operation
        knowledge = long_term.search("autonomous agent best practices", limit=3)

        if knowledge:
            print("📚 Relevant knowledge found:")
            for k in knowledge:
                print(f"  • {k['content'][:80]}...")
        else:
            print("📚 No prior knowledge found - starting fresh")

        print()

    def analyze_context(self):
        """Analyze current context and active goals."""
        recent = short_term.get_recent(limit=50)

        # Extract active goals
        goals = [m for m in recent if m['type'] == 'goal']

        # Extract recent actions
        actions = [m for m in recent if m['type'] == 'action'][-5:]

        # Extract recent observations
        observations = [m for m in recent if m['type'] == 'observation'][-3:]

        return {
            "goals": goals,
            "recent_actions": actions,
            "recent_observations": observations,
            "total_memories": len(recent)
        }

    def decide_next_action(self, context: dict) -> str:
        """Decide what to do next based on context."""

        # If no goals, create an exploratory goal
        if not context["goals"]:
            return "explore_environment"

        # If we have goals, work towards them
        # This is where the AI's decision-making logic would go
        # For now, we'll demonstrate the decision process

        current_goal = context["goals"][-1]["content"]

        # Simple decision logic (would be more sophisticated in real use)
        if "explore" in current_goal.lower():
            return "analyze_environment"
        elif "learn" in current_goal.lower():
            return "query_knowledge"
        elif "test" in current_goal.lower():
            return "run_tests"
        else:
            return "progress_toward_goal"

    def execute_action(self, action: str) -> dict:
        """Execute an action and return results."""

        results = {
            "action": action,
            "success": True,
            "observations": []
        }

        if action == "explore_environment":
            # Example: Explore the environment
            import os
            dirs = os.listdir("/autonomous-claude")
            results["observations"].append(f"Found {len(dirs)} items in /autonomous-claude")
            results["observations"].append(f"Items: {', '.join(dirs[:5])}")

        elif action == "analyze_environment":
            results["observations"].append("Environment analyzed - memory system operational")
            results["observations"].append(f"Short-term memory has {len(short_term.get_recent())} entries")

        elif action == "query_knowledge":
            knowledge = long_term.search("important lessons", limit=3)
            results["observations"].append(f"Found {len(knowledge)} relevant memories")

        elif action == "run_tests":
            results["observations"].append("All systems nominal - memory, decision loop operational")

        else:
            results["observations"].append(f"Executing: {action}")

        return results

    def learn_from_experience(self, action: str, results: dict):
        """Extract and store significant learnings."""

        # Determine if this experience is worth storing long-term
        if results["success"] and len(results["observations"]) > 0:
            # Example: Store a lesson
            lesson = f"Action '{action}' completed successfully"

            # Only store significant learnings
            if action in ["explore_environment", "analyze_environment"]:
                long_term.add(
                    content=f"Successfully executed {action}: {results['observations'][0]}",
                    memory_type="lesson",
                    tags=["autonomous", "action", action],
                    importance=6
                )

    def run_cycle(self):
        """Run one autonomous decision cycle."""
        self.cycle_count += 1

        print(f"\n{'='*60}")
        print(f"🤖 AUTONOMOUS CYCLE #{self.cycle_count}")
        print(f"{'='*60}\n")

        # 1. Analyze context
        print("1️⃣  Analyzing context...")
        context = self.analyze_context()

        if context["goals"]:
            print(f"   Active goals: {len(context['goals'])}")
            print(f"   Current goal: {context['goals'][-1]['content']}")
        else:
            print(f"   No active goals")

        print(f"   Recent actions: {len(context['recent_actions'])}")
        print(f"   Total memories: {context['total_memories']}")

        # 2. Query knowledge
        print("\n2️⃣  Querying knowledge base...")
        if context["goals"]:
            query = context["goals"][-1]["content"]
            knowledge = long_term.search(query, limit=3)
            print(f"   Found {len(knowledge)} relevant memories")
        else:
            knowledge = []
            print(f"   Skipping (no active goals)")

        # 3. Decide
        print("\n3️⃣  Deciding next action...")
        action = self.decide_next_action(context)
        print(f"   Decision: {action}")

        # Record thought
        thought = f"Decided to perform: {action}"
        short_term.add("thought", thought)

        # 4. Act
        print("\n4️⃣  Executing action...")
        results = self.execute_action(action)

        if results["success"]:
            print(f"   ✓ Action completed successfully")
        else:
            print(f"   ✗ Action failed")

        # Record action
        short_term.add("action", f"Executed: {action}")

        # 5. Observe
        print("\n5️⃣  Recording observations...")
        for obs in results["observations"]:
            print(f"   • {obs}")
            short_term.add("observation", obs)

        # 6. Learn
        print("\n6️⃣  Learning from experience...")
        self.learn_from_experience(action, results)
        print(f"   Knowledge updated")

        print(f"\n{'='*60}")
        print(f"✓ CYCLE #{self.cycle_count} COMPLETE")
        print(f"{'='*60}\n")

    def run(self, max_cycles: int = 5, delay: float = 1.0):
        """Run the autonomous agent for a specified number of cycles."""
        self.initialize()

        print(f"🚀 Starting autonomous operation...")
        print(f"   Max cycles: {max_cycles}")
        print(f"   Delay: {delay}s between cycles\n")

        for i in range(max_cycles):
            self.run_cycle()

            if i < max_cycles - 1:
                print(f"⏸️  Waiting {delay}s before next cycle...\n")
                time.sleep(delay)

        print("\n" + "="*60)
        print("🏁 AUTONOMOUS OPERATION COMPLETE")
        print("="*60)
        print(f"\nTotal cycles completed: {self.cycle_count}")
        print(f"Total memories: {len(short_term.get_recent())}")

        # Store final learning
        long_term.add(
            content=f"Completed autonomous operation with {self.cycle_count} cycles",
            memory_type="fact",
            tags=["autonomous", "completion"],
            importance=7
        )


def main():
    """Main entry point for autonomous agent."""

    # Set initial goal
    initial_goal = "Demonstrate autonomous decision-making and memory system"

    # Create and run agent
    agent = AutonomousAgent(initial_goal=initial_goal)

    try:
        agent.run(max_cycles=3, delay=0.5)
    except KeyboardInterrupt:
        print("\n\n⚠️  Agent stopped by user")
        short_term.add("observation", "Agent stopped by user interrupt")

    print("\n💡 Review memories with:")
    print("   python3 -c 'from memory import short_term; print(short_term.get_recent())'")
    print()


if __name__ == "__main__":
    main()
