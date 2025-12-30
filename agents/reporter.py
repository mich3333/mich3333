#!/usr/bin/env python3
"""
Reporter Agent - Creates documentation and summaries.
"""
from .base_agent import BaseAgent


class ReporterAgent(BaseAgent):
    """
    Reporter Agent specializes in:
    - Creating clear documentation
    - Summarizing complex information
    - Presenting results professionally
    - Writing user-friendly guides
    """

    def __init__(self, **kwargs):
        system_prompt = """You are the Reporter Agent in a multi-agent system.

Your expertise:
- Creating clear, comprehensive documentation
- Summarizing complex technical information
- Presenting results in user-friendly formats
- Writing guides, tutorials, and explanations
- Professional communication

Your documentation principles:
- Clarity over cleverness
- Examples and practical use cases
- Progressive disclosure (simple → advanced)
- Visual hierarchy with headers and formatting
- Action-oriented language

Format your reports with:
1. Executive Summary
2. Overview/Introduction
3. Detailed Sections (well-organized)
4. Examples and Usage
5. Conclusion/Next Steps

Use markdown formatting:
- Headers for structure
- Code blocks for code
- Lists for clarity
- Bold for emphasis

Make everything accessible and professional."""

        super().__init__(
            name="Reporter",
            role="Documentation & Reporting",
            system_prompt=system_prompt,
            **kwargs
        )

    def report(self, data: dict, report_type: str = "summary") -> str:
        """
        Create a report from the provided data.

        Args:
            data: The data to report on
            report_type: Type of report (summary, full, technical)

        Returns:
            Formatted report
        """
        context = {
            "report_type": report_type,
            "data": str(data)
        }

        return self.think(
            task="Create a comprehensive report from the provided data",
            context=context
        )
