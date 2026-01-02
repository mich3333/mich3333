#!/usr/bin/env python3
"""
Base Agent class for Multi-Agent System.
All specialized agents inherit from this async base class.
"""
import asyncio
import logging
import os
from collections.abc import Callable

from anthropic import AsyncAnthropic

from models.state import AgentResponse, AgentStatus, MissionContext

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Async base class for all agents in the multi-agent system.
    Features:
    - Async/await support for non-blocking operations
    - Exponential backoff retry logic
    - Shared MissionContext for inter-agent communication
    - WebSocket broadcasting for real-time updates
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        api_key: str | None = None,
        model: str = "claude-opus-4-5-20251101",
        websocket_callback: Callable | None = None
    ):
        """
        Initialize a base agent.

        Args:
            name: Agent's name (e.g., "Manager", "Researcher")
            role: Agent's role description
            system_prompt: The system prompt that defines agent behavior
            api_key: Anthropic API key (uses env var if not provided)
            model: Claude model to use
            websocket_callback: Callback for real-time WebSocket broadcasting
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model = model
        self.websocket_callback = websocket_callback

        # Initialize async Anthropic client
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                f"Agent {name}: ANTHROPIC_API_KEY not found. "
                "Set it in environment or pass as parameter."
            )

        self.client = AsyncAnthropic(api_key=self.api_key)

    async def think(
        self,
        task: str,
        context: MissionContext,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> AgentResponse:
        """
        Agent thinks about a task and returns a response (async with retry logic).

        Args:
            task: The task/question for the agent
            context: Shared MissionContext with agent memory
            max_tokens: Maximum response tokens
            temperature: Response randomness (0-1)
            max_retries: Maximum retry attempts on failure

        Returns:
            AgentResponse with success/output/error
        """
        # Log start
        context.add_log(
            agent_name=self.name,
            status=AgentStatus.IN_PROGRESS,
            message=f"Starting task: {task[:100]}...",
            thought_process="Initializing task execution"
        )
        self.log_to_websocket(self.name, "thinking", f"🤔 Analyzing: {task[:100]}...")

        # Build prompt with shared context
        prompt = self._build_prompt(task, context)

        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                # Broadcast current attempt
                if attempt > 0:
                    self.log_to_websocket(
                        self.name,
                        "retry",
                        f"🔄 Retry attempt {attempt + 1}/{max_retries}"
                    )

                # Call Claude API (async)
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )

                # Extract response text
                output = response.content[0].text

                # Log success
                context.add_log(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    message="Task completed successfully",
                    thought_process=f"Completed after {attempt + 1} attempt(s)",
                    output=output
                )
                self.log_to_websocket(self.name, "completed", "✅ Task completed")

                return AgentResponse(
                    success=True,
                    output=output,
                    thought_process=f"Completed in {attempt + 1} attempt(s)"
                )

            except Exception as e:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                logger.warning(f"{self.name}: {error_msg}. Retrying in {wait_time}s...")

                if attempt < max_retries - 1:
                    # Not final attempt - retry
                    self.log_to_websocket(
                        self.name,
                        "retry",
                        f"⚠️ {error_msg}. Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    # Final failure
                    final_error = f"Failed after {max_retries} attempts: {str(e)}"
                    context.add_log(
                        agent_name=self.name,
                        status=AgentStatus.FAILED,
                        message=final_error,
                        thought_process=f"All {max_retries} attempts exhausted"
                    )
                    self.log_to_websocket(self.name, "error", f"❌ {final_error}")

                    return AgentResponse(
                        success=False,
                        output="",
                        error=final_error
                    )

        # Should never reach here, but for type safety
        return AgentResponse(success=False, output="", error="Unknown error")

    def _build_prompt(self, task: str, context: MissionContext) -> str:
        """
        Build the prompt for the agent with shared context.

        Args:
            task: The main task
            context: MissionContext with shared findings

        Returns:
            Formatted prompt string with context
        """
        prompt = f"**Task:** {task}\n\n"

        # Add shared research findings if available
        if context.shared_findings.research_data:
            prompt += "**Available Research Findings:**\n"
            for key, value in context.shared_findings.research_data.items():
                prompt += f"- **{key}**: {value}\n"
            prompt += "\n"

        # Add code artifacts if available
        if context.shared_findings.code_artifacts:
            prompt += "**Available Code Artifacts:**\n"
            for key, value in context.shared_findings.code_artifacts.items():
                prompt += f"- **{key}**:\n```\n{value[:500]}...\n```\n"
            prompt += "\n"

        # Add review feedback if available
        if context.shared_findings.review_feedback:
            prompt += "**Review Feedback (from previous iterations):**\n"
            for i, feedback in enumerate(context.shared_findings.review_feedback, 1):
                prompt += f"{i}. {feedback}\n"
            prompt += "\n"

        # Add execution plan if available
        if context.execution_plan:
            prompt += f"**Execution Plan:** {context.execution_plan.get('analysis', 'N/A')}\n\n"

        return prompt

    def log_to_websocket(self, agent: str, status: str, message: str):
        """
        Broadcast agent's thought process to WebSocket clients.

        Args:
            agent: Agent name
            status: Status (thinking, working, completed, error, retry)
            message: Message to broadcast
        """
        if self.websocket_callback:
            try:
                self.websocket_callback(agent, status, message)
            except Exception as e:
                logger.error(f"WebSocket broadcast failed: {e}")

    def get_status(self) -> dict:
        """
        Get agent's current status.

        Returns:
            Dictionary with agent status info
        """
        return {
            "name": self.name,
            "role": self.role,
            "model": self.model,
            "ready": bool(self.api_key)
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}')>"
