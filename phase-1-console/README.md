# Console Todo App

A simple console-based todo application built with Python and cmd2.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

## Available Commands

- `list` - Show all tasks
- `add <title> [description]` - Add a new task
- `done <id>` - Mark task as complete/incomplete (toggle)
- `delete <id>` - Delete a task
- `update <id> <new_title> [new_description]` - Update a task
- `help` - Show available commands
- `quit` - Exit the application

## Examples

```
(todo) add Buy groceries
Added task #1: Buy groceries

(todo) add Call mom Remember to wish her happy birthday
Added task #2: Call mom

(todo) list
Tasks:
1. Buy groceries          [ ]
2. Call mom               [ ]

(todo) done 1
Task #1 'Buy groceries' is now completed

(todo) list
Tasks:
1. Buy groceries          [x]
2. Call mom               [ ]

(todo) update 2 Schedule doctor appointment Appointment with Dr. Smith next week
Task #2 updated successfully

(todo) delete 1
Task #1 deleted successfully

(todo) quit
```