#!/usr/bin/env python3
"""
Coder Agent - Writes code and implements solutions.
Writes code artifacts to shared MissionContext.
"""
from models.state import AgentResponse, MissionContext

from .base_agent import BaseAgent


class CoderAgent(BaseAgent):
    """
    Coder Agent specializes in:
    - Writing clean, efficient code
    - Implementing algorithms and solutions
    - Following best practices
    - Creating modular, testable code
    - **Writing code to shared_findings**
    """

    def __init__(self, **kwargs):
        system_prompt = """You are the Coder Agent in a multi-agent system.

Your expertise:
- Writing clean, efficient, production-ready code
- Following best practices and design patterns
- Creating modular, testable, maintainable code
- Proper error handling and edge cases
- Clear comments and documentation

Your principles:
- DRY (Don't Repeat Yourself)
- SOLID principles
- Clean Code practices
- Test-driven mindset
- Security awareness

Format your code responses with:
1. **Brief explanation of approach** (2-3 sentences)
2. **Well-commented code** (with docstrings)
3. **Usage examples** (how to use the code)
4. **Notes on edge cases handled**

Always write code that is:
- Readable
- Efficient
- Secure
- Well-documented

**IMPORTANT:** If you receive review feedback, carefully address ALL issues mentioned."""

        super().__init__(
            name="Coder",
            role="Code Implementation & Development",
            system_prompt=system_prompt,
            **kwargs
        )

    async def code(
        self,
        task: str,
        language: str = "python",
        context: MissionContext = None
    ) -> AgentResponse:
        """
        Write code for a specific task and save to shared_findings.

        Args:
            task: The coding task
            language: Programming language
            context: MissionContext (code written here)

        Returns:
            AgentResponse with code implementation
        """
        # Build task with language context
        full_task = f"Implement this in {language}:\n\n{task}"

        # Check if there's review feedback to address
        if context and context.shared_findings.review_feedback:
            full_task += "\n\n**CRITICAL: Address this review feedback:**\n"
            for i, feedback in enumerate(context.shared_findings.review_feedback, 1):
                full_task += f"{i}. {feedback}\n"

        response = await self.think(
            task=full_task,
            context=context
        )

        if response.success:
            # Write code artifact to shared context
            artifact_key = f"{task[:50]}_{language}"
            context.shared_findings.code_artifacts[artifact_key] = response.output
            context.shared_findings.metadata['last_language'] = language

            self.log_to_websocket(
                self.name,
                "completed",
                "💾 Code artifact saved to shared knowledge base"
            )

        return response
