---
id: 0008
title: FastAPI DB Dependency Fix
stage: red
date: 2026-01-22
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-multi-user-web-app
branch: 001-multi-user-web-app
user: WaterProof Fish
command: /sp.phr
labels: ["fastapi", "database", "dependency-injection", "contextmanager", "sqlmodel"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/db/database.py
tests:
 - none
---

## Prompt

--title "FastAPI DB Dependency Fix" --stage "red"

## Response snapshot

Fixed the FastAPI database dependency issue by removing @contextmanager decorator and converting get_session function to a plain generator function, resolving the '_GeneratorContextManager' object error that was causing crashes on POST /api/auth/signup.

## Outcome

- ✅ Impact: Resolved FastAPI dependency injection error with database sessions, allowing POST /api/auth/signup to work properly without crashes
- 🧪 Tests: none
- 📁 Files: backend/src/db/database.py (updated to remove @contextmanager and convert to plain generator function)
- 🔁 Next prompts: none
- 🧠 Reflection: FastAPI expects plain generator functions for dependency injection, not @contextmanager-wrapped generators which create _GeneratorContextManager objects incompatible with FastAPI's dependency resolution.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
