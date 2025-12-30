#!/usr/bin/env python3
"""
Coder Agent - Writes code and implements solutions.
"""
from .base_agent import BaseAgent


class CoderAgent(BaseAgent):
    """
    Coder Agent specializes in:
    - Writing clean, efficient code
    - Implementing algorithms and solutions
    - Following best practices
    - Creating modular, testable code
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
1. Brief explanation of approach
2. Well-commented code
3. Usage examples
4. Notes on edge cases handled

Always write code that is:
- Readable
- Efficient
- Secure
- Well-documented"""

        super().__init__(
            name="Coder",
            role="Code Implementation & Development",
            system_prompt=system_prompt,
            **kwargs
        )

    def code(self, task: str, language: str = "python", context: dict = None) -> str:
        """
        Write code for a specific task.

        Args:
            task: The coding task
            language: Programming language
            context: Additional context (specs, constraints, etc.)

        Returns:
            Code implementation
        """
        full_context = context or {}
        full_context['language'] = language

        return self.think(
            task=f"Implement this:\n\n{task}",
            context=full_context
        )
