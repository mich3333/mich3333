#!/usr/bin/env python3
"""
Tests for Multi-Agent System
"""
import pytest
import os
from agents import (
    BaseAgent,
    ManagerAgent,
    ResearcherAgent,
    CoderAgent,
    ReviewerAgent,
    ReporterAgent
)


# Skip tests if API key not available
pytestmark = pytest.mark.skipif(
    not os.getenv('ANTHROPIC_API_KEY'),
    reason="ANTHROPIC_API_KEY not set"
)


class TestBaseAgent:
    """Test the base agent functionality."""

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = BaseAgent(
            name="Test",
            role="Testing",
            system_prompt="You are a test agent"
        )

        assert agent.name == "Test"
        assert agent.role == "Testing"
        assert agent.api_key is not None
        assert len(agent.conversation_history) == 0

    def test_agent_status(self):
        """Test get_status method."""
        agent = BaseAgent(
            name="Test",
            role="Testing",
            system_prompt="You are a test agent"
        )

        status = agent.get_status()
        assert status['name'] == "Test"
        assert status['role'] == "Testing"
        assert status['ready'] is True

    def test_reset_conversation(self):
        """Test conversation reset."""
        agent = BaseAgent(
            name="Test",
            role="Testing",
            system_prompt="You are a test agent"
        )

        # Add some conversation
        agent.conversation_history.append({"role": "user", "content": "test"})
        assert len(agent.conversation_history) == 1

        # Reset
        agent.reset_conversation()
        assert len(agent.conversation_history) == 0


class TestSpecializedAgents:
    """Test specialized agents."""

    def test_manager_agent(self):
        """Test Manager Agent."""
        agent = ManagerAgent()
        assert agent.name == "Manager"
        assert agent.role == "Task Coordinator & Delegation"

    def test_researcher_agent(self):
        """Test Researcher Agent."""
        agent = ResearcherAgent()
        assert agent.name == "Researcher"
        assert agent.role == "Information Gathering & Analysis"

    def test_coder_agent(self):
        """Test Coder Agent."""
        agent = CoderAgent()
        assert agent.name == "Coder"
        assert agent.role == "Code Implementation & Development"

    def test_reviewer_agent(self):
        """Test Reviewer Agent."""
        agent = ReviewerAgent()
        assert agent.name == "Reviewer"
        assert agent.role == "Quality Assurance & Code Review"

    def test_reporter_agent(self):
        """Test Reporter Agent."""
        agent = ReporterAgent()
        assert agent.name == "Reporter"
        assert agent.role == "Documentation & Reporting"


class TestAgentThinking:
    """Test agent thinking capabilities (integration tests)."""

    @pytest.mark.slow
    def test_simple_task(self):
        """Test agent can complete a simple task."""
        agent = CoderAgent()
        response = agent.code(
            task="Write a function to add two numbers",
            language="python"
        )

        assert response is not None
        assert len(response) > 0
        assert 'def' in response.lower() or 'function' in response.lower()


@pytest.mark.integration
class TestOrchestrator:
    """Test the orchestrator (requires API key)."""

    @pytest.mark.slow
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes all agents."""
        from orchestrator import MultiAgentOrchestrator

        orch = MultiAgentOrchestrator()

        assert orch.manager is not None
        assert orch.researcher is not None
        assert orch.coder is not None
        assert orch.reviewer is not None
        assert orch.reporter is not None

    @pytest.mark.slow
    def test_agent_status(self):
        """Test getting all agent statuses."""
        from orchestrator import MultiAgentOrchestrator

        orch = MultiAgentOrchestrator()
        statuses = orch.get_agent_status()

        assert 'manager' in statuses
        assert 'researcher' in statuses
        assert 'coder' in statuses
        assert 'reviewer' in statuses
        assert 'reporter' in statuses


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
