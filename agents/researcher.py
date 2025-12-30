#!/usr/bin/env python3
"""
Researcher Agent - Gathers information and performs research.
"""
from .base_agent import BaseAgent


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent specializes in:
    - Information gathering
    - Analysis and research
    - Finding best practices
    - Comparing approaches
    """

    def __init__(self, **kwargs):
        system_prompt = """You are the Researcher Agent in a multi-agent system.

Your expertise:
- Thorough research and information gathering
- Analyzing different approaches and solutions
- Finding best practices and industry standards
- Comparing pros/cons of different options
- Identifying potential issues and edge cases

Your style:
- Comprehensive but concise
- Evidence-based
- Cite sources when relevant
- Consider multiple perspectives
- Highlight key findings

Format your responses with:
1. Executive Summary
2. Key Findings
3. Recommendations
4. Considerations/Risks"""

        super().__init__(
            name="Researcher",
            role="Information Gathering & Analysis",
            system_prompt=system_prompt,
            **kwargs
        )

    def research(self, topic: str, context: dict = None) -> str:
        """
        Conduct research on a specific topic.

        Args:
            topic: The research topic/question
            context: Additional context

        Returns:
            Research findings
        """
        return self.think(
            task=f"Research this topic:\n\n{topic}",
            context=context or {}
        )
