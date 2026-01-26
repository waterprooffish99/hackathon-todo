#!/usr/bin/env python3
"""Console Todo Application - A simple todo app using cmd2 for command-line interaction."""

import cmd2
from todo import TodoService


class TodoApp(cmd2.Cmd):
    """Simple todo application using cmd2."""

    intro = 'Welcome to the Todo App. Type help or ? to list commands.\n'
    prompt = '(todo) '

    def __init__(self):
        """Initialize the todo application."""
        super().__init__()
        self.service = TodoService()

    def do_add(self, arg):
        """Add a new task: add <title> [description]"""
        import shlex

        if not arg:
            self.poutput("Error: Please provide at least a title: add <title> [description]")
            return

        try:
            # Use shlex to properly parse quoted arguments
            args = shlex.split(arg)
        except ValueError:
            # Handle malformed quotes by showing error
            self.poutput("Error: Malformed quotes in command")
            return

        if len(args) < 1:
            self.poutput("Error: Please provide at least a title: add <title> [description]")
            return

        # Handle two cases:
        # Case 1: With quotes: add "title with spaces" description or add "title" "description"
        # Case 2: Without quotes: use maxsplit=1 as fallback, but with better understanding

        # If there are quoted arguments, use them as-is
        if len(args) > 1:
            # If we have 2+ arguments from shlex, first is title, rest is description
            title = args[0]
            description = ' '.join(args[1:])
        elif len(args) == 1:
            # Only one argument (likely quoted), use as title
            title = args[0]
            description = ""
        else:
            # Fallback - split on first space if no shlex parsing worked
            parts = arg.split(maxsplit=1)
            title = parts[0]
            description = parts[1] if len(parts) > 1 else ""

        task = self.service.add_task(title, description)
        output_msg = f"Added task #{task.id}: {task.title}"
        if task.description:
            output_msg += f" ({task.description})"
        self.poutput(output_msg)

    def do_list(self, arg):
        """List all tasks: list"""
        tasks = self.service.list_tasks()

        if not tasks:
            self.poutput("No tasks found.")
            return

        self.poutput("Tasks:")
        for task in tasks:
            status = "[x]" if task.completed else "[ ]"
            # Format with padding for consistent alignment
            task_line = f"{task.id}. {task.title} {status}"
            if task.description:
                task_line += f" ({task.description})"
            self.poutput(task_line)

    def do_update(self, arg):
        """Update a task: update <id> <new_title> [new_description]"""
        import shlex

        if not arg:
            self.poutput("Error: Usage: update <id> <new_title> [new_description]")
            return

        try:
            # Use shlex to properly parse quoted arguments
            args = shlex.split(arg)
        except ValueError:
            # Handle malformed quotes by showing error
            self.poutput("Error: Malformed quotes in command")
            return

        if len(args) < 2:
            self.poutput("Error: Usage: update <id> <new_title> [new_description]")
            return

        try:
            task_id = int(args[0])
        except ValueError:
            self.poutput("Error: Task ID must be a number")
            return

        # Handle the case where new_title might contain spaces
        # If there are 3+ arguments: id, new_title, new_description
        # If there are 2 arguments: id, new_title (keep old description)
        if len(args) >= 3:
            new_title = args[1]
            new_description = ' '.join(args[2:])  # Join remaining args as description
        elif len(args) == 2:
            new_title = args[1]
            new_description = None  # Don't change existing description
        else:
            self.poutput("Error: Usage: update <id> <new_title> [new_description]")
            return

        if self.service.update_task(task_id, new_title, new_description):
            task = self.service.get_task(task_id)
            if task:
                output_msg = f"Task #{task.id} updated successfully: {task.title}"
                if task.description:
                    output_msg += f" ({task.description})"
                self.poutput(output_msg)
        else:
            self.poutput(f"Error: Task not found with ID {task_id}")

    def do_delete(self, arg):
        """Delete a task: delete <id>"""
        if not arg:
            self.poutput("Error: Please provide a task ID: delete <id>")
            return

        try:
            task_id = int(arg)
        except ValueError:
            self.poutput("Error: Task ID must be a number")
            return

        if self.service.delete_task(task_id):
            self.poutput(f"Task #{task_id} deleted successfully")
        else:
            self.poutput(f"Error: Task not found with ID {task_id}")

    def do_done(self, arg):
        """Mark a task as complete/incomplete: done <id>"""
        if not arg:
            self.poutput("Error: Please provide a task ID: done <id>")
            return

        try:
            task_id = int(arg)
        except ValueError:
            self.poutput("Error: Task ID must be a number")
            return

        if self.service.toggle_complete(task_id):
            task = self.service.get_task(task_id)
            if task:
                status = "completed" if task.completed else "not completed"
                self.poutput(f"Task #{task.id} '{task.title}' is now {status}")
        else:
            self.poutput(f"Error: Task not found with ID {task_id}")

    def do_quit(self, arg):
        """Quit the application: quit"""
        return True

    def help_add(self):
        """Help for add command."""
        self.poutput("add <title> [description] - Add a new task")

    def help_list(self):
        """Help for list command."""
        self.poutput("list - Show all tasks with ID, title, and completion status")

    def help_update(self):
        """Help for update command."""
        self.poutput("update <id> <new_title> [new_description] - Update a task by ID")

    def help_delete(self):
        """Help for delete command."""
        self.poutput("delete <id> - Delete a task by ID")

    def help_done(self):
        """Help for done command."""
        self.poutput("done <id> - Mark a task as complete/incomplete (toggle)")

    def help_quit(self):
        """Help for quit command."""
        self.poutput("quit - Exit the application")


if __name__ == '__main__':
    app = TodoApp()
    app.cmdloop()