#!/usr/bin/env python3
"""
Manager Agent - Coordinates the multi-agent system.
Breaks down complex tasks and delegates to specialized agents.
"""
from .base_agent import BaseAgent


class ManagerAgent(BaseAgent):
    """
    Manager Agent coordinates the entire system.
    - Analyzes complex tasks
    - Breaks them into subtasks
    - Delegates to appropriate agents
    - Ensures quality and completion
    """

    def __init__(self, **kwargs):
        system_prompt = """You are the Manager Agent in a multi-agent system.

Your role:
1. Analyze complex tasks from users
2. Break them down into clear, actionable subtasks
3. Delegate subtasks to specialized agents:
   - Researcher: For gathering information, research, analysis
   - Coder: For writing code, algorithms, technical implementation
   - Reviewer: For quality assurance, testing, code review
   - Reporter: For documentation, summaries, final presentations

4. Coordinate the workflow and ensure all pieces work together

Your output format:
{
  "analysis": "Brief analysis of the task",
  "subtasks": [
    {"agent": "researcher", "task": "Research X", "priority": 1},
    {"agent": "coder", "task": "Implement Y", "priority": 2},
    {"agent": "reviewer", "task": "Review Z", "priority": 3},
    {"agent": "reporter", "task": "Document results", "priority": 4}
  ],
  "estimated_time": "2-3 hours",
  "complexity": "medium"
}

Be clear, concise, and strategic. Think step-by-step."""

        super().__init__(
            name="Manager",
            role="Task Coordinator & Delegation",
            system_prompt=system_prompt,
            **kwargs
        )

    def break_down_task(self, user_task: str) -> dict:
        """
        Break down a complex user task into subtasks.

        Args:
            user_task: The complex task from the user

        Returns:
            Dictionary with task breakdown and delegation plan
        """
        response = self.think(
            task=f"Analyze and break down this task:\n\n{user_task}",
            context={"format": "JSON with analysis and subtasks"}
        )

        # Parse the response (in production, you'd want better JSON extraction)
        return {
            "original_task": user_task,
            "manager_response": response,
            "status": "planned"
        }
