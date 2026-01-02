#!/usr/bin/env python3
"""
Shared State Models for Multi-Agent System.
Defines MissionContext - the centralized memory for all agents.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class ReviewDecision(str, Enum):
    """Reviewer decision outcomes."""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class AgentLog(BaseModel):
    """Individual agent log entry with thought process."""
    agent_name: str
    status: AgentStatus
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    thought_process: str | None = None  # Internal reasoning
    output: str | None = None  # Actual deliverable

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SharedFindings(BaseModel):
    """Shared knowledge base between agents."""
    research_data: dict[str, str] = Field(default_factory=dict)
    code_artifacts: dict[str, str] = Field(default_factory=dict)
    review_feedback: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MissionContext(BaseModel):
    """
    Centralized mission state shared across all agents.
    Acts as the "memory" of the multi-agent system.
    """
    # Core identifiers
    task_id: str = Field(..., description="Unique task identifier")
    original_prompt: str = Field(..., description="User's original task")

    # Execution state
    current_status: Literal[
        "planning", "executing", "reviewing", "completed", "failed", "cancelled"
    ] = "planning"
    current_agent: str | None = None

    # Shared memory
    agent_logs: list[AgentLog] = Field(default_factory=list)
    shared_findings: SharedFindings = Field(default_factory=SharedFindings)

    # Workflow tracking
    execution_plan: dict[str, Any] | None = None  # Manager's JSON plan
    retry_count: int = 0
    max_retries: int = 3

    # Feedback loop state
    review_decision: ReviewDecision | None = None
    review_iteration: int = 0
    max_iterations: int = 2

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def add_log(
        self,
        agent_name: str,
        status: AgentStatus,
        message: str,
        thought_process: str | None = None,
        output: str | None = None
    ):
        """Add a log entry and update timestamp."""
        log = AgentLog(
            agent_name=agent_name,
            status=status,
            message=message,
            thought_process=thought_process,
            output=output
        )
        self.agent_logs.append(log)
        self.updated_at = datetime.utcnow()
        self.current_agent = agent_name

    def update_status(self, status: str):
        """Update mission status."""
        self.current_status = status  # type: ignore
        self.updated_at = datetime.utcnow()
        if status in ["completed", "failed", "cancelled"]:
            self.completed_at = datetime.utcnow()

    def can_retry(self) -> bool:
        """Check if retry is allowed."""
        return self.retry_count < self.max_retries

    def increment_retry(self):
        """Increment retry counter."""
        self.retry_count += 1
        self.updated_at = datetime.utcnow()

    def can_iterate_review(self) -> bool:
        """Check if review iteration is allowed."""
        return self.review_iteration < self.max_iterations

    def increment_review_iteration(self):
        """Increment review iteration counter."""
        self.review_iteration += 1
        self.updated_at = datetime.utcnow()


class AgentResponse(BaseModel):
    """Structured agent response."""
    success: bool
    output: str
    thought_process: str | None = None
    error: str | None = None
