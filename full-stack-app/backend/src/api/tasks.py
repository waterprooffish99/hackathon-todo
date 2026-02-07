from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from typing import List, Optional
from src.db.database import get_session
from src.skills.task_crud_skill import TaskCrudSkill
from src.skills.auth_skill import AuthSkill
from src.middleware.auth import get_current_user, require_user_match
from src.models.user import User
from src.models.task import Task
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["tasks"])

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCompletionUpdate(BaseModel):
    completed: bool

class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total_count: int
    page: int
    limit: int

@router.get("/tasks", response_model=TaskListResponse)
def get_tasks_authenticated_user(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Retrieve all tasks for the authenticated user.

    Args:
        session: Database session
        current_user: Currently authenticated user (extracted from JWT)
        completed: Optional filter for completion status
        limit: Number of tasks to return
        offset: Number of tasks to skip

    Returns:
        TaskListResponse: List of tasks and metadata

    Raises:
        HTTPException: If unauthorized
    """
    tasks = TaskCrudSkill.get_tasks_for_user(
        user_id=current_user.id,
        session=session,
        completed=completed,
        limit=limit,
        offset=offset
    )

    # Convert to response format
    task_responses = []
    for task in tasks:
        task_response = TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        task_responses.append(task_response)

    total_count = TaskCrudSkill.get_task_count_for_user(current_user.id, session, completed)

    return TaskListResponse(
        tasks=task_responses,
        total_count=total_count,
        page=(offset // limit) + 1,
        limit=limit
    )


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
def get_tasks(
    user_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Retrieve all tasks for a specific user.

    Args:
        user_id: UUID of the user whose tasks to retrieve
        session: Database session
        current_user: Currently authenticated user
        completed: Optional filter for completion status
        limit: Number of tasks to return
        offset: Number of tasks to skip

    Returns:
        TaskListResponse: List of tasks and metadata

    Raises:
        HTTPException: If user ID mismatch or unauthorized
    """
    # Verify that the user_id in path matches the JWT user_id
    require_user_match(str(current_user.id), str(user_id))

    tasks = TaskCrudSkill.get_tasks_for_user(
        user_id=user_id,
        session=session,
        completed=completed,
        limit=limit,
        offset=offset
    )

    # Convert to response format
    task_responses = []
    for task in tasks:
        task_response = TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        task_responses.append(task_response)

    total_count = TaskCrudSkill.get_task_count_for_user(user_id, session, completed)

    return TaskListResponse(
        tasks=task_responses,
        total_count=total_count,
        page=(offset // limit) + 1,
        limit=limit
    )


@router.post("/tasks", response_model=TaskResponse)
def create_task_authenticated_user(
    task_create: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task for the authenticated user.

    Args:
        task_create: Task creation data
        session: Database session
        current_user: Currently authenticated user (extracted from JWT)

    Returns:
        TaskResponse: Created task details

    Raises:
        HTTPException: If unauthorized
    """
    task = TaskCrudSkill.create_task(
        user_id=current_user.id,
        title=task_create.title,
        description=task_create.description,
        session=session
    )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.post("/{user_id}/tasks", response_model=TaskResponse)
def create_task(
    user_id: UUID,
    task_create: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task for a user.

    Args:
        user_id: UUID of the user to create task for
        task_create: Task creation data
        session: Database session
        current_user: Currently authenticated user

    Returns:
        TaskResponse: Created task details

    Raises:
        HTTPException: If user ID mismatch or unauthorized
    """
    # Verify that the user_id in path matches the JWT user_id
    require_user_match(str(current_user.id), str(user_id))

    task = TaskCrudSkill.create_task(
        user_id=user_id,
        title=task_create.title,
        description=task_create.description,
        session=session
    )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task_authenticated_user(
    task_id: UUID,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing task for the authenticated user.

    Args:
        task_id: UUID of the task to update
        task_update: Task update data
        session: Database session
        current_user: Currently authenticated user (extracted from JWT)

    Returns:
        TaskResponse: Updated task details

    Raises:
        HTTPException: If task not found or unauthorized
    """
    task = TaskCrudSkill.update_task(
        task_id=task_id,
        user_id=current_user.id,
        session=session,
        title=task_update.title,
        description=task_update.description
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: UUID,
    task_id: UUID,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing task for a user.

    Args:
        user_id: UUID of the user who owns the task
        task_id: UUID of the task to update
        task_update: Task update data
        session: Database session
        current_user: Currently authenticated user

    Returns:
        TaskResponse: Updated task details

    Raises:
        HTTPException: If user ID mismatch, task not found, or unauthorized
    """
    # Verify that the user_id in path matches the JWT user_id
    require_user_match(str(current_user.id), str(user_id))

    task = TaskCrudSkill.update_task(
        task_id=task_id,
        user_id=user_id,
        session=session,
        title=task_update.title,
        description=task_update.description
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.delete("/tasks/{task_id}")
def delete_task_authenticated_user(
    task_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task for the authenticated user.

    Args:
        task_id: UUID of the task to delete
        session: Database session
        current_user: Currently authenticated user (extracted from JWT)

    Raises:
        HTTPException: If task not found or unauthorized
    """
    success = TaskCrudSkill.delete_task(
        task_id=task_id,
        user_id=current_user.id,
        session=session
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"message": "Task deleted successfully"}


@router.delete("/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: UUID,
    task_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task for a user.

    Args:
        user_id: UUID of the user who owns the task
        task_id: UUID of the task to delete
        session: Database session
        current_user: Currently authenticated user

    Raises:
        HTTPException: If user ID mismatch, task not found, or unauthorized
    """
    # Verify that the user_id in path matches the JWT user_id
    require_user_match(str(current_user.id), str(user_id))

    success = TaskCrudSkill.delete_task(
        task_id=task_id,
        user_id=user_id,
        session=session
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"message": "Task deleted successfully"}


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def toggle_task_completion_authenticated_user(
    task_id: UUID,
    completion_update: TaskCompletionUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle the completion status of a task for the authenticated user.

    Args:
        task_id: UUID of the task to update
        completion_update: Completion status update
        session: Database session
        current_user: Currently authenticated user (extracted from JWT)

    Returns:
        TaskResponse: Updated task details

    Raises:
        HTTPException: If task not found or unauthorized
    """
    task = TaskCrudSkill.toggle_task_completion(
        task_id=task_id,
        user_id=current_user.id,
        completed=completion_update.completed,
        session=session
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
def toggle_task_completion(
    user_id: UUID,
    task_id: UUID,
    completion_update: TaskCompletionUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle the completion status of a task.

    Args:
        user_id: UUID of the user who owns the task
        task_id: UUID of the task to update
        completion_update: Completion status update
        session: Database session
        current_user: Currently authenticated user

    Returns:
        TaskResponse: Updated task details

    Raises:
        HTTPException: If user ID mismatch, task not found, or unauthorized
    """
    # Verify that the user_id in path matches the JWT user_id
    require_user_match(str(current_user.id), str(user_id))

    task = TaskCrudSkill.toggle_task_completion(
        task_id=task_id,
        user_id=user_id,
        completed=completion_update.completed,
        session=session
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
        updated_at=task.updated_at
    )