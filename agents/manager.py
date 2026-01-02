#!/usr/bin/env python3
"""
Manager Agent - Coordinates the multi-agent system.
Breaks down complex tasks into structured JSON plans.
"""
import json
import re
from typing import Any

from models.state import MissionContext

from .base_agent import BaseAgent


class ManagerAgent(BaseAgent):
    """
    Manager Agent coordinates the entire system.
    - Analyzes complex tasks
    - Breaks them into subtasks (strict JSON format)
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

**CRITICAL: You MUST respond with ONLY valid JSON in this exact format:**

{
  "analysis": "Brief analysis of the task (1-2 sentences)",
  "subtasks": [
    {"agent": "researcher", "task": "Research X", "priority": 1},
    {"agent": "coder", "task": "Implement Y based on research", "priority": 2},
    {"agent": "reviewer", "task": "Review the implementation for bugs and quality", "priority": 3},
    {"agent": "reporter", "task": "Document the final solution", "priority": 4}
  ],
  "estimated_complexity": "low|medium|high",
  "requires_iteration": true
}

**Rules:**
- ONLY output valid JSON (no markdown, no code blocks, no explanations)
- Agent names must be lowercase: researcher, coder, reviewer, reporter
- Priority determines execution order (1 = first)
- Analysis should be concise and strategic
- Estimated complexity helps set expectations
- Set requires_iteration to true if you expect Reviewer → Coder feedback loop

Be clear, concise, and strategic. Think step-by-step."""

        super().__init__(
            name="Manager",
            role="Task Coordinator & Delegation",
            system_prompt=system_prompt,
            **kwargs
        )

    async def break_down_task(
        self,
        user_task: str,
        context: MissionContext
    ) -> dict[str, Any]:
        """
        Break down a complex user task into structured JSON plan.

        Args:
            user_task: The complex task from the user
            context: Shared MissionContext

        Returns:
            Dictionary with parsed JSON plan
        """
        response = await self.think(
            task=f"Analyze and create execution plan for:\n\n{user_task}",
            context=context
        )

        if not response.success:
            return {
                "error": response.error,
                "analysis": "Failed to create plan",
                "subtasks": [],
                "estimated_complexity": "unknown",
                "requires_iteration": False
            }

        # Extract and parse JSON from response
        plan = self._extract_json(response.output)

        # Store plan in context
        context.execution_plan = plan
        context.update_status("executing")

        return plan

    def _extract_json(self, text: str) -> dict[str, Any]:
        """
        Extract and parse JSON from agent response.

        Args:
            text: Agent's response text

        Returns:
            Parsed JSON dictionary
        """
        try:
            # Try to find JSON in the response
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)

            # Find JSON object
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group()
                plan = json.loads(json_str)

                # Validate structure
                if 'subtasks' in plan and isinstance(plan['subtasks'], list):
                    return plan

        except json.JSONDecodeError as e:
            print(f"⚠️ Manager JSON parse error: {e}")

        # Fallback: Create a default plan
        return {
            "analysis": "Using default workflow (JSON parsing failed)",
            "subtasks": [
                {
                    "agent": "researcher",
                    "task": "Research and analyze the requirements",
                    "priority": 1
                },
                {
                    "agent": "coder",
                    "task": "Implement the solution based on research",
                    "priority": 2
                },
                {
                    "agent": "reviewer",
                    "task": "Review the implementation for quality and correctness",
                    "priority": 3
                },
                {
                    "agent": "reporter",
                    "task": "Create final documentation and summary",
                    "priority": 4
                }
            ],
            "estimated_complexity": "medium",
            "requires_iteration": True
        }
