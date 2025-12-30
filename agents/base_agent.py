#!/usr/bin/env python3
"""
Base Agent class for Multi-Agent System.
All specialized agents inherit from this base class.
"""
import os
from typing import Optional, Dict, List
from anthropic import Anthropic


class BaseAgent:
    """
    Base class for all agents in the multi-agent system.
    Each agent has a name, role, and specialized system prompt.
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        api_key: Optional[str] = None,
        model: str = "claude-opus-4-5-20251101"
    ):
        """
        Initialize a base agent.

        Args:
            name: Agent's name (e.g., "Manager", "Researcher")
            role: Agent's role description
            system_prompt: The system prompt that defines agent behavior
            api_key: Anthropic API key (uses env var if not provided)
            model: Claude model to use
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model = model

        # Initialize Anthropic client
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                f"Agent {name}: ANTHROPIC_API_KEY not found. "
                "Set it in environment or pass as parameter."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history: List[Dict] = []

    def think(
        self,
        task: str,
        context: Optional[Dict] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """
        Agent thinks about a task and returns a response.

        Args:
            task: The task/question for the agent
            context: Additional context (optional)
            max_tokens: Maximum response tokens
            temperature: Response randomness (0-1)

        Returns:
            Agent's response as string
        """
        # Build the prompt
        prompt = self._build_prompt(task, context)

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.system_prompt,
                messages=self.conversation_history,
                temperature=temperature
            )

            # Extract response text
            assistant_message = response.content[0].text

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            error_msg = f"Error in {self.name}: {str(e)}"
            print(f"⚠️ {error_msg}")
            return f"[Error: {error_msg}]"

    def _build_prompt(self, task: str, context: Optional[Dict] = None) -> str:
        """
        Build the prompt for the agent.

        Args:
            task: The main task
            context: Additional context

        Returns:
            Formatted prompt string
        """
        prompt = f"Task: {task}"

        if context:
            prompt += "\n\nContext:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"

        return prompt

    def reset_conversation(self):
        """Reset the agent's conversation history."""
        self.conversation_history = []

    def get_status(self) -> Dict:
        """
        Get agent's current status.

        Returns:
            Dictionary with agent status info
        """
        return {
            "name": self.name,
            "role": self.role,
            "model": self.model,
            "conversation_length": len(self.conversation_history),
            "ready": bool(self.api_key)
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}')>"
