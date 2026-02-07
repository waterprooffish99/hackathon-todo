from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import Session
from datetime import datetime
import json

from ..models import Task, User
from ..services import TaskService
from ..database import get_session
from ..auth import get_current_user
from ..schemas import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(tags=["tasks"])


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    due_from: Optional[datetime] = Query(None, description="Filter tasks with due date from this date"),
    due_to: Optional[datetime] = Query(None, description="Filter tasks with due date to this date"),
    sort_by: Optional[str] = Query("created_date", description="Sort by field"),
    order: Optional[str] = Query("asc", description="Sort order"),
    page: Optional[int] = Query(1, description="Page number for pagination"),
    limit: Optional[int] = Query(50, description="Number of items per page")
):
    """
    List user tasks with advanced filtering.
    """
    task_service = TaskService(session)

    # Get all tasks for the current user
    tasks = task_service.list_by_user(current_user.user_id)

    # Apply filters
    if status:
        if status.lower() == "pending":
            tasks = [task for task in tasks if not task.completed]
        elif status.lower() == "completed":
            tasks = [task for task in tasks if task.completed]
        elif status.lower() == "all":
            # Don't filter - return all tasks
            pass

    if priority:
        # Assuming priority is already validated by the schema
        filtered_tasks = []
        for task in tasks:
            if hasattr(task, 'priority') and task.priority and str(task.priority.value).lower() == priority.lower():
                filtered_tasks.append(task)
        tasks = filtered_tasks

    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
        # Use the service method to filter by tags
        filtered_tasks = []
        for task in tasks:
            if task.tags:  # If task has tags
                import json
                try:
                    task_tags = json.loads(task.tags) if isinstance(task.tags, str) else task.tags
                    if task_tags and any(tag in task_tags for tag in tag_list):
                        filtered_tasks.append(task)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat tags as a comma-separated string
                    task_tags = task.tags.split(',') if isinstance(task.tags, str) else []
                    if any(tag.strip() in [t.strip() for t in task_tags] for tag in tag_list):
                        filtered_tasks.append(task)
        tasks = filtered_tasks

    if due_from or due_to:
        filtered_tasks = []
        for task in tasks:
            if task.due_at:
                if due_from and task.due_at < due_from:
                    continue
                if due_to and task.due_at > due_to:
                    continue
            filtered_tasks.append(task)
        tasks = filtered_tasks

    # Apply sorting
    tasks = task_service.sort_tasks(tasks, sort_by, order)

    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_tasks = tasks[start_idx:end_idx]

    # Convert tasks to response format
    response_tasks = []
    for task in paginated_tasks:
        response_tasks.append(TaskResponse(
            task_id=str(task.id),
            title=task.title,
            description=task.description,
            priority=getattr(task, 'priority', None),
            tags=task.tags,
            due_at=task.due_at,
            remind_at=task.remind_at,
            recurrence_rule=getattr(task, 'recurrence_rule', None),
            completed=task.completed,
            completion_date=getattr(task, 'completed_at', None),
            user_id=str(task.user_id),
            created_at=task.created_at,
            updated_at=task.updated_at,
            version=1
        ))

    return response_tasks


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_create: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task with advanced features.
    """
    task_service = TaskService(session)

    # Convert tags list to JSON string
    tags_json = json.dumps(task_create.tags) if task_create.tags else None

    # Create task object
    task = Task(
        title=task_create.title,
        description=task_create.description,
        priority=task_create.priority,
        tags=tags_json,
        due_at=task_create.due_at,
        remind_at=task_create.remind_at,
        recurrence_rule=task_create.recurrence_rule,
        user_id=current_user.user_id
    )

    try:
        created_task = task_service.create(task)
        # Manually construct response to ensure field name compatibility
        return TaskResponse(
            task_id=str(created_task.id),
            title=created_task.title,
            description=created_task.description,
            priority=created_task.priority,
            tags=created_task.tags,
            due_at=created_task.due_at,
            remind_at=created_task.remind_at,
            recurrence_rule=created_task.recurrence_rule,
            completed=created_task.completed,
            completion_date=getattr(created_task, 'completed_at', None),
            user_id=str(created_task.user_id),
            created_at=created_task.created_at,
            updated_at=created_task.updated_at,
            version=1
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,  # UUID as string
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific task.
    """
    task_service = TaskService(session)

    # We need to convert the string to UUID for comparison
    # For now, using a simple approach
    import uuid
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    task = task_service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify user owns the task
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Manually construct response to ensure field name compatibility
    return TaskResponse(
        task_id=str(task.id),
        title=task.title,
        description=task.description,
        priority=task.priority,
        tags=task.tags,
        due_at=task.due_at,
        remind_at=task.remind_at,
        recurrence_rule=task.recurrence_rule,
        completed=task.completed,
        completion_date=getattr(task, 'completed_at', None),
        user_id=str(task.user_id),
        created_at=task.created_at,
        updated_at=task.updated_at,
        version=1
    )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a task.
    """
    task_service = TaskService(session)

    # We need to convert the string to UUID for comparison
    import uuid
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    task = task_service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify user owns the task
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Prepare update data
    update_data = task_update.dict(exclude_unset=True)

    # Convert tags to JSON string if provided
    if 'tags' in update_data and update_data['tags'] is not None:
        update_data['tags'] = json.dumps(update_data['tags'])

    # Update task
    try:
        updated_task = task_service.update(task_id, Task(**update_data))
        # Manually construct response to ensure field name compatibility
        return TaskResponse(
            task_id=str(updated_task.id),
            title=updated_task.title,
            description=updated_task.description,
            priority=updated_task.priority,
            tags=updated_task.tags,
            due_at=updated_task.due_at,
            remind_at=updated_task.remind_at,
            recurrence_rule=updated_task.recurrence_rule,
            completed=updated_task.completed,
            completion_date=getattr(updated_task, 'completed_at', None),
            user_id=str(updated_task.user_id),
            created_at=updated_task.created_at,
            updated_at=updated_task.updated_at,
            version=1
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task.
    """
    task_service = TaskService(session)

    # We need to convert the string to UUID for comparison
    import uuid
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    task = task_service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify user owns the task
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Access denied")

    success = task_service.delete(task_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete task")

    return {"message": "Task deleted successfully"}


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def mark_task_complete(
    task_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a task as complete.
    """
    task_service = TaskService(session)

    # We need to convert the string to UUID for comparison
    import uuid
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    task = task_service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify user owns the task
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Access denied")

    completed_task = task_service.mark_complete(task_id)
    if not completed_task:
        raise HTTPException(status_code=500, detail="Failed to mark task as complete")

    # Manually construct response to ensure field name compatibility
    return TaskResponse(
        task_id=str(completed_task.id),
        title=completed_task.title,
        description=completed_task.description,
        priority=completed_task.priority,
        tags=completed_task.tags,
        due_at=completed_task.due_at,
        remind_at=completed_task.remind_at,
        recurrence_rule=completed_task.recurrence_rule,
        completed=completed_task.completed,
        completion_date=getattr(completed_task, 'completed_at', None),
        user_id=str(completed_task.user_id),
        created_at=completed_task.created_at,
        updated_at=completed_task.updated_at,
        version=1
    )


@router.get("/tasks/search", response_model=List[TaskResponse])
async def search_tasks(
    q: str = Query(..., min_length=1, description="Search query string"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    page: Optional[int] = Query(1, description="Page number for pagination"),
    limit: Optional[int] = Query(50, description="Number of items per page")
):
    """
    Search tasks by content.
    """
    task_service = TaskService(session)

    tasks = task_service.search_tasks(current_user.user_id, q)

    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_tasks = tasks[start_idx:end_idx]

    return paginated_tasks