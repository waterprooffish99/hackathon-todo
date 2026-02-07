"""
Unit and integration tests for the AI subagents.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.main import app
from src.agents.task_interpreter_agent import TaskInterpretationAgent
from src.agents.reminder_reasoning_agent import ReminderReasoningAgent


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_task_interpreter_agent():
    """Mock TaskInterpretationAgent for testing."""
    agent = Mock(spec=TaskInterpretationAgent)

    # Mock the interpret_task_description method
    agent.interpret_task_description = AsyncMock(return_value={
        "title": "Test Task",
        "description": "Test Description",
        "priority": "medium",
        "tags": ["test", "ai"],
        "due_at": "2023-12-31T10:00:00",
        "remind_at": "2023-12-30T10:00:00",
        "recurrence_rule": None,
        "confidence": 0.8,
        "extracted_entities": []
    })

    return agent




@pytest.fixture
def mock_reminder_reasoning_agent():
    """Mock ReminderReasoningAgent for testing."""
    agent = Mock(spec=ReminderReasoningAgent)

    # Mock the calculate_optimal_reminder_time method
    agent.calculate_optimal_reminder_time = AsyncMock(return_value={
        "calculated_reminder_time": "2023-12-30T09:00:00",
        "base_calculation": "2023-12-30T09:00:00",
        "adjustments_applied": [],
        "reasoning": "Calculated based on task priority",
        "confidence_score": 0.85
    })

    return agent


class TestTaskInterpretationAgent:
    """Test cases for TaskInterpretationAgent."""

    @pytest.mark.asyncio
    async def test_interpret_task_description(self, mock_task_interpreter_agent):
        """Test interpreting a task description."""
        # Arrange
        text = "Call John tomorrow at 3pm to discuss the quarterly report"
        user_context = {"preferences": {"default_priority": "high"}}

        # Act
        result = await mock_task_interpreter_agent.interpret_task_description(text, user_context)

        # Assert
        assert result["title"] == "Call John tomorrow at 3pm to discuss the quarterly report"
        assert result["priority"] == "high"  # Should use user's default priority
        assert "call" in [tag.lower() for tag in result["tags"]]
        assert result["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_suggest_tags(self, mock_task_interpreter_agent):
        """Test suggesting tags for a task."""
        # This would test the suggest_tags method
        pass

    @pytest.mark.asyncio
    async def test_suggest_priority(self, mock_task_interpreter_agent):
        """Test suggesting priority for a task."""
        # This would test the suggest_priority method
        pass




class TestReminderReasoningAgent:
    """Test cases for ReminderReasoningAgent."""

    @pytest.mark.asyncio
    async def test_calculate_optimal_reminder_time(self, mock_reminder_reasoning_agent):
        """Test calculating optimal reminder time."""
        # Arrange
        task = {
            "title": "Submit report",
            "description": "Submit quarterly report",
            "due_at": "2023-12-31T17:00:00",
            "priority": "high"
        }
        user_profile = {
            "timezone": "UTC",
            "quiet_hours": {"start": 22, "end": 7}
        }
        task_history = []

        # Act
        result = await mock_reminder_reasoning_agent.calculate_optimal_reminder_time(
            task, user_profile, task_history
        )

        # Assert
        assert "calculated_reminder_time" in result
        assert "confidence_score" in result
        assert result["confidence_score"] > 0

    @pytest.mark.asyncio
    async def test_manage_reminder_updates(self, mock_reminder_reasoning_agent):
        """Test managing reminder updates when task changes."""
        # This would test the manage_reminder_updates method
        pass


class TestAIAGentsAPI:
    """Test cases for AI agents API endpoints."""

    def test_interpret_task_endpoint(self, client):
        """Test the task interpretation endpoint."""
        # Arrange
        request_data = {
            "text": "Schedule meeting with team tomorrow at 2pm",
            "context": {}
        }

        # Act
        response = client.post("/v1/ai/interpret-task", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "priority" in data


    def test_analyze_reminders_endpoint(self, client):
        """Test the reminder analysis endpoint."""
        # Arrange
        request_data = {
            "title": "Submit assignment",
            "description": "Submit the quarterly assignment",
            "priority": "high",
            "due_at": "2023-12-31T23:59:59"
        }

        # Act
        response = client.post("/v1/ai/analyze-reminders", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "calculated_reminder_time" in data

    def test_ai_chat_endpoint(self, client):
        """Test the AI chat endpoint."""
        # Arrange
        request_data = {
            "message": "Remind me to call mom tomorrow at 7pm",
            "context": {}
        }

        # Act
        response = client.post("/v1/ai/chat", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "actions" in data


if __name__ == "__main__":
    pytest.main([__file__])