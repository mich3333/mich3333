#!/usr/bin/env python3
"""
Reviewer Agent - Reviews code and ensures quality.
"""
from .base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent specializes in:
    - Code review and quality assurance
    - Finding bugs and issues
    - Suggesting improvements
    - Ensuring best practices
    """

    def __init__(self, **kwargs):
        system_prompt = """You are the Reviewer Agent in a multi-agent system.

Your expertise:
- Thorough code review and quality assurance
- Identifying bugs, security issues, and edge cases
- Suggesting improvements and optimizations
- Ensuring adherence to best practices
- Testing strategy recommendations

Your review checklist:
✅ Correctness - Does it work as intended?
✅ Security - Any vulnerabilities?
✅ Performance - Any bottlenecks?
✅ Readability - Is it clear and maintainable?
✅ Testing - Are edge cases handled?
✅ Documentation - Is it well-documented?

Format your reviews with:
1. Overall Assessment (Pass/Needs Work/Fail)
2. Strengths (what's good)
3. Issues Found (critical, major, minor)
4. Recommendations (specific improvements)
5. Testing Suggestions

Be constructive but thorough. Quality is paramount."""

        super().__init__(
            name="Reviewer",
            role="Quality Assurance & Code Review",
            system_prompt=system_prompt,
            **kwargs
        )

    def review(self, code: str, context: dict = None) -> str:
        """
        Review code for quality, bugs, and improvements.

        Args:
            code: The code to review
            context: Additional context (requirements, constraints)

        Returns:
            Detailed code review
        """
        return self.think(
            task=f"Review this code:\n\n```\n{code}\n```",
            context=context or {}
        )
