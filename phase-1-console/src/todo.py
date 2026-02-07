class Task:
    """Represents a single task in the todo application."""

    def __init__(self, title, description=""):
        self.id = 0  # Will be set by TodoService
        self.title = title
        self.description = description
        self.completed = False


class TodoService:
    """Service class to manage tasks in memory."""

    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title, description=""):
        """Add a new task with the given title and optional description."""
        task = Task(title, description)
        task.id = self.next_id
        self.next_id += 1
        self.tasks.append(task)
        return task

    def list_tasks(self):
        """Return a list of all tasks."""
        return self.tasks

    def update_task(self, task_id, new_title=None, new_description=None):
        """Update a task with the given ID."""
        for task in self.tasks:
            if task.id == task_id:
                if new_title is not None:
                    task.title = new_title
                if new_description is not None:
                    task.description = new_description
                return True
        return False

    def delete_task(self, task_id):
        """Delete a task with the given ID."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                return True
        return False

    def toggle_complete(self, task_id):
        """Toggle the completion status of a task with the given ID."""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = not task.completed
                return True
        return False

    def get_task(self, task_id):
        """Get a specific task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None