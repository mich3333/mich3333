#!/usr/bin/env python3
"""
Researcher Agent - Gathers information and performs research.
Writes findings to shared MissionContext.
"""
from models.state import AgentResponse, MissionContext

from .base_agent import BaseAgent


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent specializes in:
    - Information gathering
    - Analysis and research
    - Finding best practices
    - Comparing approaches
    - **Writing findings to shared_findings**
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
1. **Executive Summary** (2-3 sentences)
2. **Key Findings** (bulleted list)
3. **Recommendations** (specific, actionable)
4. **Considerations/Risks** (potential issues)

Be thorough but focused. Your research will be used by the Coder and Reviewer agents."""

        super().__init__(
            name="Researcher",
            role="Information Gathering & Analysis",
            system_prompt=system_prompt,
            **kwargs
        )

    async def research(
        self,
        topic: str,
        context: MissionContext
    ) -> AgentResponse:
        """
        Conduct research on a specific topic and write to shared_findings.

        Args:
            topic: The research topic/question
            context: MissionContext (findings written here)

        Returns:
            AgentResponse with research results
        """
        response = await self.think(
            task=f"Research this topic:\n\n{topic}",
            context=context
        )

        if response.success:
            # Write research findings to shared context
            context.shared_findings.research_data[topic] = response.output
            context.shared_findings.metadata['last_research'] = topic

            self.log_to_websocket(
                self.name,
                "completed",
                "📚 Research findings saved to shared knowledge base"
            )

        return response
