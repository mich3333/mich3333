#!/usr/bin/env python3
"""
Reviewer Agent - Reviews code and provides Approve/Reject decisions.
Implements feedback loop logic.
"""
import re

from models.state import AgentResponse, MissionContext, ReviewDecision

from .base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent specializes in:
    - Code review and quality assurance
    - Finding bugs and issues
    - **Approve/Reject decisions**
    - Suggesting improvements
    - **Writing feedback to shared_findings**
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

**CRITICAL: You MUST start your response with ONE of these decisions:**
- **APPROVED** - Code is production-ready
- **REJECTED** - Critical issues found, must be rewritten
- **NEEDS_REVISION** - Minor issues, coder should fix

Format your reviews:
1. **Decision:** APPROVED | REJECTED | NEEDS_REVISION
2. **Summary:** (one sentence overall assessment)
3. **Strengths:** (what's good)
4. **Issues Found:** (critical, major, minor - be specific)
5. **Recommendations:** (concrete improvements)
6. **Testing Suggestions:** (what to test)

Be constructive but thorough. Quality is paramount.
If you REJECT or request NEEDS_REVISION, provide specific, actionable feedback."""

        super().__init__(
            name="Reviewer",
            role="Quality Assurance & Code Review",
            system_prompt=system_prompt,
            **kwargs
        )

    async def review(
        self,
        task_description: str,
        context: MissionContext
    ) -> tuple[AgentResponse, ReviewDecision]:
        """
        Review code and return decision (APPROVED/REJECTED/NEEDS_REVISION).

        Args:
            task_description: Description of what to review
            context: MissionContext with code artifacts

        Returns:
            Tuple of (AgentResponse, ReviewDecision)
        """
        # Get latest code artifact
        code_artifacts = context.shared_findings.code_artifacts
        if not code_artifacts:
            return (
                AgentResponse(
                    success=False,
                    output="No code to review",
                    error="No code artifacts found in shared_findings"
                ),
                ReviewDecision.REJECTED
            )

        # Get the most recent code
        latest_code = list(code_artifacts.values())[-1]

        response = await self.think(
            task=f"Review this code:\n\n```\n{latest_code}\n```\n\nTask was: {task_description}",
            context=context
        )

        if not response.success:
            return response, ReviewDecision.REJECTED

        # Extract decision from response
        decision = self._extract_decision(response.output)

        # Store decision in context
        context.review_decision = decision

        # If not approved, add feedback to shared findings
        if decision != ReviewDecision.APPROVED:
            feedback = self._extract_feedback(response.output)
            context.shared_findings.review_feedback.append(feedback)

            self.log_to_websocket(
                self.name,
                "warning" if decision == ReviewDecision.NEEDS_REVISION else "error",
                f"📋 Review: {decision.value.upper()} - Feedback added to shared findings"
            )
        else:
            self.log_to_websocket(
                self.name,
                "completed",
                "✅ Review: APPROVED - Code meets quality standards"
            )

        return response, decision

    def _extract_decision(self, review_text: str) -> ReviewDecision:
        """
        Extract decision from review text.

        Args:
            review_text: Reviewer's response

        Returns:
            ReviewDecision enum
        """
        text_upper = review_text.upper()

        if "APPROVED" in text_upper or "✅ APPROVED" in text_upper:
            return ReviewDecision.APPROVED
        elif "REJECTED" in text_upper or "❌ REJECTED" in text_upper:
            return ReviewDecision.REJECTED
        elif "NEEDS_REVISION" in text_upper or "NEEDS REVISION" in text_upper:
            return ReviewDecision.NEEDS_REVISION
        else:
            # Default to needs_revision if unclear
            return ReviewDecision.NEEDS_REVISION

    def _extract_feedback(self, review_text: str) -> str:
        """
        Extract actionable feedback from review.

        Args:
            review_text: Reviewer's response

        Returns:
            Concise feedback string
        """
        # Try to extract "Issues Found" and "Recommendations" sections
        issues_match = re.search(
            r'\*\*Issues Found:\*\*(.*?)(?:\*\*|$)',
            review_text,
            re.DOTALL | re.IGNORECASE
        )
        recommendations_match = re.search(
            r'\*\*Recommendations:\*\*(.*?)(?:\*\*|$)',
            review_text,
            re.DOTALL | re.IGNORECASE
        )

        feedback = []
        if issues_match:
            feedback.append(f"Issues: {issues_match.group(1).strip()}")
        if recommendations_match:
            feedback.append(f"Recommendations: {recommendations_match.group(1).strip()}")

        return " | ".join(feedback) if feedback else review_text[:500]
