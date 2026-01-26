---
id: 003
title: Create Tasks
stage: tasks
date: 2026-01-18
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-evolution
branch: 001-todo-evolution
user: WaterProof Fish
command: sp.tasks
labels: [tasks, todo, evolution, phase1]
links:
  spec: specs/001-todo-evolution/spec.md
  plan: specs/001-todo-evolution/plan.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-todo-evolution/tasks.md
tests:
 - none
---

## Prompt

```text
Create tasks for Phase 1 only - In-Memory Python Console Todo App
Make very small, easy steps. Do NOT do Phase 2, 3, 4 or 5 now.

Task 1. Project folder structure
Create this basic folder structure:

hackathon-todo-phase1/
├── specs/
│   └── phase1-basic-features.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── todo.py
├── README.md
└── requirements.txt

Task 2. Basic requirements.txt
Create requirements.txt with just one line:
cmd2==2.4.3

Task 3. Simple Task class
In src/todo.py create a very simple class:

class Task:
    def __init__(self, title, description=""):
        self.title = title
        self.description = description
        self.completed = False
        self.id = 0   # we will set real id later

Task 4. Todo service with memory list
In src/todo.py add:

class TodoService:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title, description=""):
        task = Task(title, description)
        task.id = self.next_id
        self.next_id += 1
        self.tasks.append(task)
        return task

    def list_tasks(self):
        return self.tasks

    # We will add more methods later

Task 5. Basic console commands - Part 1
Create src/main.py with cmd2
Make these commands work:
- list     → show all tasks with id and title
- add <title> [description] → add new task
- quit     → exit program

Task 6. Show nice list format
When user types "list", show something like:

Tasks:
1. Buy milk               [ ]
2. Call mom               [x]

( [ ] = not done, [x] = done )

Task 7. Finish basic commands - Part 2
Add these commands:
- done <id>     → mark task as completed
- delete <id>   → remove task by id
- update <id> <new title> [new description] → change title and/or description

Task 8. Final polish & README
- Add simple help text for each command
- Make README.md with these sections:
  - Project name
  - How to install (uv pip install -r requirements.txt)
  - How to run (python src/main.py)
  - List of commands with examples

Important rules for Phase 1:
- Only Python code
- No database
- No web
- No FastAPI
- No Next.js
- Keep everything very simple
- Use only the 5 basic features: add, list, update, delete, mark complete
```

## Response snapshot

Generated comprehensive tasks file for Phase 1 of the Evolution of Todo project. The tasks.md file contains 25 specific, actionable tasks organized in phases: Setup (T001-T006), Foundational (T007-T008), User Story 1 implementation (T009-T022), and Polish (T023-T025). The tasks follow the required checklist format with proper IDs, story labels, and file paths. The implementation focuses on the core basic todo management functionality (add, list, update, delete, mark complete) using Python and cmd2 as specified. Tasks are organized to enable parallel execution where possible and follow a logical dependency order.

## Outcome

- ✅ Impact: Complete task breakdown for Phase 1 implementation ready for execution
- 🧪 Tests: none
- 📁 Files: specs/001-todo-evolution/tasks.md
- 🔁 Next prompts: Ready for implementation following the task list
- 🧠 Reflection: Tasks are well-structured following the checklist format and enabling parallel execution

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): standard tasks generation
- Next experiment (smallest change to try): Begin implementation following the task list