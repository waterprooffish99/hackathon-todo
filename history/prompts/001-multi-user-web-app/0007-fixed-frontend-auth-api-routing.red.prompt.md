---
id: 0007
title: Fixed Frontend Auth API Routing
stage: red
date: 2026-01-20
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-multi-user-web-app
branch: 001-multi-user-web-app
user: WaterProof Fish
command: /sp.phr
labels: ["frontend", "auth", "api", "routing", "nextjs", "backend-integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/app/login/page.tsx
  - frontend/app/signup/page.tsx
tests:
  - POST /api/auth/signup
  - POST /api/auth/login
---

## Prompt

--title "Fixed-Frontend-Auth-API-Routing" --stage "red"

## Response snapshot

Successfully fixed frontend auth API calls by changing relative paths to absolute URLs using NEXT_PUBLIC_API_BASE_URL environment variable.

## Outcome

- ✅ Impact: Fixed 404 errors on auth API calls by routing requests to backend instead of Next.js handling them locally
- 🧪 Tests: Auth API calls now properly reach backend and return 200/201 instead of 404
- 📁 Files: Modified frontend/app/login/page.tsx and frontend/app/signup/page.tsx to use absolute URLs
- 🔁 Next prompts: None needed - auth flow is now fully functional
- 🧠 Reflection: Environment variables provide flexible configuration for API routing across different environments

## Evaluation notes (flywheel)

- Failure modes observed: None - all fixes worked as expected
- Graders run and results (PASS/FAIL): PASS - auth API calls now properly route to backend
- Prompt variant (if applicable): Standard API routing fix prompt
- Next experiment (smallest change to try): Add API request error handling improvements
