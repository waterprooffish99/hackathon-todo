---
id: 001
title: Fix bcrypt password validation and dependency issues
stage: general
date: 2026-01-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 001-multi-user-web-app
user: WaterProof Fish
command: /sp.implement
labels: ["authentication", "security", "validation", "dependencies"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/skills/auth_skill.py
  - backend/src/api/auth.py
  - backend/pyproject.toml
tests:
  - test_password_validation.py
---

## Prompt

We are stabilizing Hackathon II – Phase 3 using Spec-Kit Plus. The backend is now running correctly, but signup fails with a runtime error during password hashing.

Observed Error:
ValueError: password cannot be longer than 72 bytes
Additionally, warnings indicate bcrypt backend incompatibility:
AttributeError: module 'bcrypt' has no attribute '__about__'

Root Causes:
1. bcrypt version incompatibility with Python 3.12 and passlib
2. Password length constraints (bcrypt max 72 bytes) are not enforced at the skill/spec level
3. Backend crashes during hashing, causing misleading CORS errors in the browser

Required Fix (authoritative and complete):

PART 1 — Dependency Stability
- Ensure bcrypt is pinned to a version compatible with passlib on Python 3.12
- Use UV-compatible dependency declaration
- Do NOT downgrade Python
- Do NOT remove passlib
- Ensure passlib can correctly detect bcrypt backend

PART 2 — AuthSkill Password Validation
- Update AuthSkill.get_password_hash (or equivalent) to enforce bcrypt constraints
- Validate password length BEFORE hashing
- If password exceeds bcrypt limits:
  - Raise a clean, user-safe validation error (HTTP 400)
  - Do NOT truncate silently
- Keep hashing secure and deterministic

PART 3 — Spec Compliance
- Keep changes minimal and localized
- Do NOT modify routes except to propagate clean errors
- Do NOT touch JWT logic, MCP tools, chat agent, or frontend
- Ensure failure returns JSON error response (not server crash)

Acceptance Criteria:
- Signup with valid password succeeds
- Signup with too-long password returns HTTP 400 with clear message
- No passlib/bcrypt warnings on startup
- No 500 errors during signup
- CORS errors disappear naturally
- System is stable to continue Phase 3 and Phase 4

## Response snapshot

Fixed the bcrypt password hashing issue by implementing the required changes:

PART 1 — Dependency Stability:
- Updated pyproject.toml to pin bcrypt to version 4.0.1 which is compatible with passlib on Python 3.13
- Added "bcrypt==4.0.1" to the dependencies list

PART 2 — AuthSkill Password Validation:
- Updated AuthSkill.get_password_hash() to validate password length before hashing
- Added check to ensure password length doesn't exceed 72 bytes (the bcrypt limit)
- Raises ValueError with clear message if password is too long

PART 3 — API Error Handling:
- Updated the signup endpoint in auth.py to catch ValueError exceptions
- Added proper HTTP 400 error response for password validation failures
- Maintained clean error propagation without server crashes

The implementation ensures that:
- Signup with valid passwords (≤72 bytes) succeeds
- Signup with too-long passwords returns HTTP 400 with clear error message
- No more passlib/bcrypt warnings on startup after installing bcrypt==4.0.1
- No more 500 errors during signup due to password length issues
- System is now stable for continued development

## Outcome

- ✅ Impact: Fixed bcrypt incompatibility and added password length validation to prevent server crashes during signup
- 🧪 Tests: Created and ran password validation tests confirming correct behavior
- 📁 Files: Modified auth_skill.py, auth.py, and pyproject.toml with minimal, targeted changes
- 🔁 Next prompts: Ready for continued Phase 3 and Phase 4 development
- 🧠 Reflection: Proper input validation at the boundary prevents downstream crashes and improves user experience

## Evaluation notes (flywheel)

- Failure modes observed: Previously, long passwords caused server crashes with 500 errors instead of proper validation
- Graders run and results (PASS/FAIL): PASS - all validation tests pass and dependencies are resolved
- Prompt variant (if applicable): Standard implementation prompt
- Next experiment (smallest change to try): Continue with Phase 3 and Phase 4 development