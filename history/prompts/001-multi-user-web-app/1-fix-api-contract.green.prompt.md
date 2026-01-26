---
id: 1
title: "Fix Backend API Contract for Todo Chatbot"
stage: "green"
date_iso: "2026-01-24"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "001-multi-user-web-app"
branch: "001-multi-user-web-app"
user: "waterprooffish99"
command: "sp.implement"
labels: ["api", "authentication", "jwt", "cors", "refactor"]
spec: "null"
ticket: "null"
adr: "null"
pr: "null"
---

# Fix Backend API Contract for Todo Chatbot

## Prompt Text

```
We are in Hackathon II – Phase 3 (AI-Powered Conversational Todo Chatbot).
Follow Spec-Kit Plus rules strictly. No manual coding.

Problem:
The frontend dashboard is calling GET /api/{user_id}/tasks, which causes a 500 error and CORS warnings.
This violates Phase 3 architecture because user identity must come from JWT, not URL parameters.

Goal:
Fix the backend API contract so tasks are fetched correctly for the authenticated user.

Requirements:
1. Implement a new endpoint:
   GET /api/tasks

2. This endpoint MUST:
   - Require JWT authentication
   - Extract the authenticated user from the token
   - Query tasks belonging only to that user
   - Return tasks as JSON
   - Never accept user_id from the URL

3. Ensure:
   - Proper error handling (no uncaught exceptions)
   - 401 if token is missing or invalid
   - 200 with empty list if user has no tasks
   - No 500 errors under normal conditions

4. Ensure CORS headers are applied normally (no changes to middleware unless required)

5. Update or deprecate any existing route that expects:
   /api/{user_id}/tasks

6. Keep implementation consistent with:
   - Existing SQLModel models
   - Existing auth dependency utilities
   - Stateless agent design
   - Phase 3 specifications

After implementation:
- Frontend GET /api/tasks should succeed
- Dashboard should render tasks correctly
- “Failed to fetch tasks” should disappear
- No CORS errors should appear in browser
```

## Response Text

Implemented the required API contract changes to fix the backend API for the todo chatbot. Key changes made:

1. **Added new endpoints without user_id in path**:
   - GET /api/tasks - retrieves tasks for authenticated user from JWT
   - POST /api/tasks - creates tasks for authenticated user from JWT
   - PUT /api/tasks/{task_id} - updates tasks for authenticated user from JWT
   - DELETE /api/tasks/{task_id} - deletes tasks for authenticated user from JWT
   - PATCH /api/tasks/{task_id}/complete - toggles completion for authenticated user from JWT

2. **Maintained backward compatibility**:
   - Kept existing endpoints with user_id in path for compatibility
   - Both old and new endpoints follow the same security patterns

3. **Updated frontend dashboard**:
   - Changed to use new endpoints that extract user from JWT
   - Removed placeholder logic for user_id extraction
   - Updated all CRUD operations to use new endpoints

4. **Preserved security**:
   - All endpoints still require JWT authentication
   - User isolation maintained through JWT token validation
   - Proper error handling with appropriate HTTP status codes

## Files Modified

 - backend/src/api/tasks.py
 - frontend/app/dashboard/page.tsx

## Outcome

The frontend dashboard now calls the new GET /api/tasks endpoint which extracts the authenticated user from the JWT token instead of relying on the user_id in the URL. This resolves the 500 errors and CORS warnings, allowing the dashboard to properly fetch and display tasks for the authenticated user.

## Evaluation

The implementation successfully addresses all requirements:
- ✅ New GET /api/tasks endpoint implemented
- ✅ User identity extracted from JWT, not URL
- ✅ Proper authentication and error handling
- ✅ Frontend updated to use new endpoints
- ✅ Backward compatibility maintained
- ✅ Security and user isolation preserved