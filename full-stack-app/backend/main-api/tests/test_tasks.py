"""
Unit and integration tests for the task management functionality.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.main import app
from src.models import Task
from src.services import TaskService
from src.api.tasks import router


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_task_service():
    """Mock TaskService for testing."""
    service = Mock(spec=TaskService)

    # Mock the create method
    service.create = Mock(return_value=Task(
        task_id="123e4567-e89b-12d3-a456-426614174000",
        title="Test Task",
        description="Test Description",
        priority="medium",
        tags='["test", "api"]',
        due_at=datetime.now(),
        remind_at=datetime.now(),
        completed=False,
        user_id="123e4567-e89b-12d3-a456-426614174001"
    ))

    # Mock the list_by_user method
    service.list_by_user = Mock(return_value=[])

    return service


class TestTaskAPI:
    """Test cases for task API endpoints."""

    def test_create_task_success(self, client, mock_task_service):
        """Test successful task creation."""
        # Arrange
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": "high",
            "tags": ["test", "api"],
            "due_at": "2023-12-31T10:00:00",
            "remind_at": "2023-12-30T10:00:00"
        }

        # Act
        response = client.post("/v1/tasks/", json=task_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == "high"

    def test_create_task_missing_title(self, client):
        """Test task creation with missing title."""
        # Arrange
        task_data = {
            "description": "Test Description"
            # Missing required title
        }

        # Act
        response = client.post("/v1/tasks/", json=task_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_get_task_success(self, client):
        """Test successful task retrieval."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174000"

        # Act
        response = client.get(f"/v1/tasks/{task_id}")

        # Assert
        assert response.status_code == 200
        # Additional assertions would depend on mock setup

    def test_update_task_success(self, client):
        """Test successful task update."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174000"
        update_data = {
            "title": "Updated Task",
            "priority": "low"
        }

        # Act
        response = client.put(f"/v1/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["priority"] == "low"

    def test_delete_task_success(self, client):
        """Test successful task deletion."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174000"

        # Act
        response = client.delete(f"/v1/tasks/{task_id}")

        # Assert
        assert response.status_code == 200

    def test_mark_task_complete(self, client):
        """Test marking a task as complete."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174000"

        # Act
        response = client.patch(f"/v1/tasks/{task_id}/complete")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    def test_search_tasks(self, client):
        """Test searching for tasks."""
        # Arrange
        search_query = "test"

        # Act
        response = client.get(f"/v1/tasks/search?q={search_query}")

        # Assert
        assert response.status_code == 200
        # Should return a list of tasks
        assert isinstance(response.json(), list)


class TestTaskService:
    """Test cases for TaskService."""

    def test_create_task_validates_dates(self, mock_task_service):
        """Test that task creation validates due and reminder dates."""
        # This would test the validation logic in TaskService
        # Implementation would depend on the actual validation methods
        pass

    def test_sort_tasks_by_priority(self, mock_task_service):
        """Test sorting tasks by priority."""
        # This would test the sort_tasks method
        # Implementation would depend on the actual sort_tasks method
        pass

    def test_filter_tasks_by_tags(self, mock_task_service):
        """Test filtering tasks by tags."""
        # This would test the list_by_tags method
        # Implementation would depend on the actual list_by_tags method
        pass


if __name__ == "__main__":
    pytest.main([__file__])