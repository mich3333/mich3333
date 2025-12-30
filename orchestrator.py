#!/usr/bin/env python3
"""
Orchestrator - Coordinates the multi-agent system.
Manages agent workflow and collaboration.
"""
import json
import re
from typing import Dict, List, Optional
from agents import (
    ManagerAgent,
    ResearcherAgent,
    CoderAgent,
    ReviewerAgent,
    ReporterAgent
)


class MultiAgentOrchestrator:
    """
    Orchestrates multiple AI agents to solve complex tasks.

    Workflow:
    1. User submits a complex task
    2. Manager breaks it down into subtasks
    3. Specialized agents work on their subtasks
    4. Reporter summarizes the results
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the orchestrator and all agents.

        Args:
            api_key: Anthropic API key (optional, uses env var if not provided)
        """
        self.api_key = api_key

        # Initialize all agents
        self.manager = ManagerAgent(api_key=api_key)
        self.researcher = ResearcherAgent(api_key=api_key)
        self.coder = CoderAgent(api_key=api_key)
        self.reviewer = ReviewerAgent(api_key=api_key)
        self.reporter = ReporterAgent(api_key=api_key)

        # Agent registry
        self.agents = {
            'manager': self.manager,
            'researcher': self.researcher,
            'coder': self.coder,
            'reviewer': self.reviewer,
            'reporter': self.reporter
        }

        # Execution log
        self.execution_log: List[Dict] = []

    def execute_task(self, user_task: str) -> Dict:
        """
        Execute a complex task using the multi-agent system.

        Args:
            user_task: The task from the user

        Returns:
            Dictionary with execution results and logs
        """
        self.execution_log = []

        # Step 1: Manager analyzes and breaks down the task
        self._log("manager", "analyzing", "Analyzing task and creating plan...")
        plan = self.manager.break_down_task(user_task)
        self._log("manager", "completed", plan['manager_response'])

        # Step 2: Extract subtasks from manager's response
        subtasks = self._extract_subtasks(plan['manager_response'])

        # Step 3: Execute subtasks with appropriate agents
        results = {}
        for subtask in subtasks:
            agent_name = subtask.get('agent', 'researcher').lower()
            task_description = subtask.get('task', '')

            if agent_name in self.agents:
                agent = self.agents[agent_name]
                self._log(agent_name, "working", f"Working on: {task_description}")

                try:
                    # Execute the subtask
                    result = agent.think(task_description)
                    results[agent_name] = result
                    self._log(agent_name, "completed", result)
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    results[agent_name] = error_msg
                    self._log(agent_name, "error", error_msg)

        # Step 4: Reporter creates final summary
        self._log("reporter", "working", "Creating final report...")
        final_report = self.reporter.report({
            "original_task": user_task,
            "plan": plan['manager_response'],
            "results": results
        }, report_type="full")
        self._log("reporter", "completed", final_report)

        return {
            "task": user_task,
            "plan": plan,
            "subtask_results": results,
            "final_report": final_report,
            "execution_log": self.execution_log,
            "status": "completed"
        }

    def _extract_subtasks(self, manager_response: str) -> List[Dict]:
        """
        Extract subtasks from manager's response.

        Args:
            manager_response: The manager's task breakdown

        Returns:
            List of subtasks
        """
        # Try to extract JSON if present
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', manager_response)
            if json_match:
                data = json.loads(json_match.group())
                if 'subtasks' in data:
                    return data['subtasks']
        except:
            pass

        # Fallback: Create a simple workflow
        return [
            {"agent": "researcher", "task": "Research and analyze the requirements", "priority": 1},
            {"agent": "coder", "task": "Implement the solution", "priority": 2},
            {"agent": "reviewer", "task": "Review the implementation", "priority": 3},
        ]

    def _log(self, agent: str, status: str, message: str):
        """
        Log an agent's action.

        Args:
            agent: Agent name
            status: Status (analyzing, working, completed, error)
            message: Log message
        """
        log_entry = {
            "agent": agent,
            "status": status,
            "message": message,
            "timestamp": self._get_timestamp()
        }
        self.execution_log.append(log_entry)

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def get_agent_status(self) -> Dict:
        """
        Get status of all agents.

        Returns:
            Dictionary with all agent statuses
        """
        return {
            name: agent.get_status()
            for name, agent in self.agents.items()
        }

    def reset_all_agents(self):
        """Reset conversation history for all agents."""
        for agent in self.agents.values():
            agent.reset_conversation()

        self.execution_log = []
