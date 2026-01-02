#!/usr/bin/env python3
"""
Orchestrator - Coordinates the multi-agent system with feedback loops.
Implements Reviewer → Coder retry logic for quality assurance.
"""
import uuid
from collections.abc import Callable
from typing import Any

from agents import CoderAgent, ManagerAgent, ReporterAgent, ResearcherAgent, ReviewerAgent
from models.state import MissionContext, ReviewDecision


class MultiAgentOrchestrator:
    """
    Orchestrates multiple AI agents with feedback loops.

    Features:
    - Async execution for concurrent operations
    - Shared MissionContext for inter-agent communication
    - Reviewer → Coder feedback loop
    - Real-time WebSocket broadcasting
    - Task cancellation support
    """

    def __init__(
        self,
        api_key: str | None = None,
        websocket_callback: Callable | None = None
    ):
        """
        Initialize the orchestrator and all agents.

        Args:
            api_key: Anthropic API key (optional, uses env var if not provided)
            websocket_callback: Callback for real-time WebSocket updates
        """
        self.api_key = api_key
        self.websocket_callback = websocket_callback
        self.active_tasks: dict[str, MissionContext] = {}
        self.cancelled_tasks: set = set()

        # Initialize all agents with WebSocket callback
        self.manager = ManagerAgent(api_key=api_key, websocket_callback=websocket_callback)
        self.researcher = ResearcherAgent(api_key=api_key, websocket_callback=websocket_callback)
        self.coder = CoderAgent(api_key=api_key, websocket_callback=websocket_callback)
        self.reviewer = ReviewerAgent(api_key=api_key, websocket_callback=websocket_callback)
        self.reporter = ReporterAgent(api_key=api_key, websocket_callback=websocket_callback)

        # Agent registry
        self.agents = {
            'manager': self.manager,
            'researcher': self.researcher,
            'coder': self.coder,
            'reviewer': self.reviewer,
            'reporter': self.reporter
        }

    async def execute_task(self, user_task: str) -> dict[str, Any]:
        """
        Execute a complex task using the multi-agent system with feedback loops.

        Args:
            user_task: The task from the user

        Returns:
            Dictionary with execution results and complete context
        """
        # Create MissionContext
        task_id = str(uuid.uuid4())[:8]
        context = MissionContext(
            task_id=task_id,
            original_prompt=user_task
        )

        # Store active task
        self.active_tasks[task_id] = context

        try:
            # Step 1: Manager creates execution plan
            self._broadcast("manager", "planning", "🎯 Creating execution plan...")
            plan = await self.manager.break_down_task(user_task, context)

            if 'error' in plan:
                context.update_status("failed")
                return self._build_response(context, error=plan['error'])

            # Step 2: Execute subtasks in priority order
            subtasks = sorted(plan.get('subtasks', []), key=lambda x: x.get('priority', 99))

            for subtask in subtasks:
                # Check if task was cancelled
                if task_id in self.cancelled_tasks:
                    context.update_status("cancelled")
                    self._broadcast("system", "cancelled", "🛑 Task cancelled by user")
                    return self._build_response(context, error="Task cancelled by user")

                agent_name = subtask.get('agent', 'researcher').lower()
                task_description = subtask.get('task', '')

                # Execute based on agent type
                if agent_name == 'researcher':
                    await self._execute_researcher(task_description, context)

                elif agent_name == 'coder':
                    # Coder → Reviewer feedback loop
                    await self._execute_coder_with_review(task_description, context)

                elif agent_name == 'reviewer':
                    # Standalone review (if needed)
                    await self._execute_reviewer(task_description, context)

                elif agent_name == 'reporter':
                    # Reporter is handled separately at the end
                    pass

            # Step 3: Final report
            self._broadcast("reporter", "working", "📝 Creating final report...")
            report_response = await self.reporter.report(
                task_summary=f"Executed {len(subtasks)} subtasks",
                context=context
            )

            # Mark as completed
            context.update_status("completed")

            return self._build_response(
                context,
                final_report=report_response.output if report_response.success else "Report generation failed"
            )

        except Exception as e:
            context.update_status("failed")
            self._broadcast("system", "error", f"❌ System error: {str(e)}")
            return self._build_response(context, error=str(e))

        finally:
            # Cleanup
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            if task_id in self.cancelled_tasks:
                self.cancelled_tasks.remove(task_id)

    async def _execute_researcher(self, task: str, context: MissionContext):
        """Execute researcher task."""
        self._broadcast("researcher", "working", f"🔍 Researching: {task[:100]}...")
        response = await self.researcher.research(task, context)

        if not response.success:
            self._broadcast("researcher", "error", f"❌ Research failed: {response.error}")

    async def _execute_coder_with_review(self, task: str, context: MissionContext):
        """
        Execute coder task with review feedback loop.

        Logic:
        1. Coder writes code
        2. Reviewer reviews code
        3. If REJECTED/NEEDS_REVISION → send back to Coder (with feedback)
        4. Repeat until APPROVED or max iterations reached
        """
        max_iterations = context.max_iterations

        for iteration in range(max_iterations + 1):
            # Check if this is a retry
            if iteration > 0:
                context.increment_review_iteration()
                self._broadcast(
                    "coder",
                    "retry",
                    f"🔄 Coder iteration {iteration + 1}/{max_iterations + 1} (addressing feedback)"
                )

            # Coder writes/revises code
            self._broadcast("coder", "working", f"💻 Writing code: {task[:100]}...")
            coder_response = await self.coder.code(task, "python", context)

            if not coder_response.success:
                self._broadcast("coder", "error", f"❌ Coding failed: {coder_response.error}")
                break

            # Reviewer reviews the code
            self._broadcast("reviewer", "working", "🔎 Reviewing code quality...")
            review_response, decision = await self.reviewer.review(task, context)

            if not review_response.success:
                self._broadcast("reviewer", "error", f"❌ Review failed: {review_response.error}")
                break

            # Check decision
            if decision == ReviewDecision.APPROVED:
                self._broadcast("reviewer", "completed", "✅ Code APPROVED - Quality standards met")
                break

            elif decision == ReviewDecision.REJECTED and iteration < max_iterations:
                self._broadcast(
                    "reviewer",
                    "warning",
                    f"❌ Code REJECTED - Sending back to Coder (iteration {iteration + 1}/{max_iterations})"
                )
                # Feedback already added to context.shared_findings.review_feedback
                continue

            elif decision == ReviewDecision.NEEDS_REVISION and iteration < max_iterations:
                self._broadcast(
                    "reviewer",
                    "warning",
                    f"⚠️ Code needs revision - Sending back to Coder (iteration {iteration + 1}/{max_iterations})"
                )
                continue

            else:
                # Max iterations reached
                self._broadcast(
                    "reviewer",
                    "warning",
                    f"⏱️ Max review iterations reached ({max_iterations}). Proceeding with current version."
                )
                break

    async def _execute_reviewer(self, task: str, context: MissionContext):
        """Execute standalone reviewer task."""
        self._broadcast("reviewer", "working", f"🔎 Reviewing: {task[:100]}...")
        response, decision = await self.reviewer.review(task, context)

        if not response.success:
            self._broadcast("reviewer", "error", f"❌ Review failed: {response.error}")

    def cancel_task(self, task_id: str):
        """Cancel an active task."""
        if task_id in self.active_tasks:
            self.cancelled_tasks.add(task_id)
            self._broadcast("system", "cancelled", f"🛑 Cancelling task {task_id}...")

    def _broadcast(self, agent: str, status: str, message: str):
        """Broadcast message to WebSocket clients."""
        if self.websocket_callback:
            try:
                self.websocket_callback(agent, status, message)
            except Exception as e:
                print(f"WebSocket broadcast error: {e}")

    def _build_response(
        self,
        context: MissionContext,
        final_report: str | None = None,
        error: str | None = None
    ) -> dict[str, Any]:
        """Build final response dictionary."""
        return {
            "task_id": context.task_id,
            "task": context.original_prompt,
            "status": context.current_status,
            "execution_plan": context.execution_plan,
            "final_report": final_report,
            "error": error,
            "review_decision": context.review_decision.value if context.review_decision else None,
            "review_iterations": context.review_iteration,
            "agent_logs": [
                {
                    "agent": log.agent_name,
                    "status": log.status.value,
                    "message": log.message,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in context.agent_logs
            ],
            "shared_findings": {
                "research_count": len(context.shared_findings.research_data),
                "code_artifacts_count": len(context.shared_findings.code_artifacts),
                "review_feedback_count": len(context.shared_findings.review_feedback)
            },
            "execution_time": (
                (context.completed_at - context.created_at).total_seconds()
                if context.completed_at else None
            )
        }

    def get_agent_status(self) -> dict[str, Any]:
        """Get status of all agents."""
        return {
            name: agent.get_status()
            for name, agent in self.agents.items()
        }

    def get_active_tasks(self) -> list[str]:
        """Get list of active task IDs."""
        return list(self.active_tasks.keys())
