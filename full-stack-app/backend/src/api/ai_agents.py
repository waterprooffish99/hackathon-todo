"""
API endpoints for AI subagents in the Cloud-Native AI Todo Platform.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from sqlmodel import Session
from pydantic import BaseModel

from ..models import Task
from ..db.database import get_session
from .auth import get_current_user
from ..agents.task_interpreter_agent import task_interpreter_agent
from ..agents.reminder_reasoning_agent import reminder_reasoning_agent
from ..schemas import TaskCreate, TaskResponse


class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] = {}


class InterpretTaskRequest(BaseModel):
    text: str
    context: Dict[str, Any] = {}


router = APIRouter(prefix="/v1/ai", tags=["ai-agents"])


@router.post("/interpret-task")
async def interpret_task(
    request: InterpretTaskRequest,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Process natural language input to extract task properties and structure.
    """
    try:
        interpreted_task = await task_interpreter_agent.interpret_task_description(request.text, request.context)
        return interpreted_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error interpreting task: {str(e)}")




@router.post("/analyze-reminders")
async def analyze_reminders(
    task_data: TaskCreate,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Calculate optimal reminder timing based on task type and user behavior.
    """
    try:
        # Get user profile (in a real implementation, this would fetch from database)
        user_profile = {
            "timezone": "UTC",
            "quiet_hours": {"start": 22, "end": 7},
            "preferred_notification_times": ["09:00", "12:00", "18:00"],
            "notification_methods": ["email", "push"]
        }

        # Create a mock task history for the agent
        task_history = []

        # Create a task object for the agent
        task_obj = {
            "title": task_data.title,
            "description": task_data.description,
            "due_at": task_data.due_at.isoformat() if task_data.due_at else None,
            "priority": task_data.priority,
            "category": "general"  # Would be determined by the system
        }

        reminder_analysis = await reminder_reasoning_agent.calculate_optimal_reminder_time(
            task_obj,
            user_profile,
            task_history
        )

        return reminder_analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing reminders: {str(e)}")


@router.post("/chat")
async def ai_chat_interface(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    AI-powered chat interface for natural language interaction with the todo system.
    """
    try:
        # This would typically route to the appropriate AI agent based on the message content
        # For now, we'll interpret it as a task
        interpreted_task = await task_interpreter_agent.interpret_task_description(request.message, request.context)

        # If the message seems to be creating a task, return the interpretation
        if interpreted_task.get("title"):
            return {
                "response": f"I understood you want to create a task: '{interpreted_task['title']}'",
                "actions": ["task_creation_proposal"],
                "task_suggestion": interpreted_task
            }
        else:
            return {
                "response": "I understood your request but need more information to take action.",
                "actions": ["request_clarification"],
                "understanding": interpreted_task
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing chat message: {str(e)}")