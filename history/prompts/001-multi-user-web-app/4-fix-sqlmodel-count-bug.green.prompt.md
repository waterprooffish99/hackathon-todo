---
id: 4
title: "Fix SQLModel Count Bug in Task CRUD Skill"
stage: "green"
date_iso: "2026-01-24"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "001-multi-user-web-app"
branch: "001-multi-user-web-app"
user: "waterprooffish99"
command: "sp.implement"
labels: ["sqlmodel", "database", "bug-fix", "count-query", "sqlalchemy"]
spec: "null"
ticket: "null"
adr: "null"
pr: "null"
---

# Fix SQLModel Count Bug in Task CRUD Skill

## Prompt Text

```
Fix the SQLModel count bug causing 500 errors in GET /api/tasks.

Context:
- Backend uses SQLModel + SQLAlchemy 2.x
- Error: AttributeError: 'ScalarResult' object has no attribute 'count'
- File: backend/src/skills/task_crud_skill.py
- Method: get_task_count_for_user

Root Cause:
session.exec(query) returns ScalarResult, which does not support .count() in SQLAlchemy 2.x.

Required Fix (must follow exactly):
1. Replace usage of `.count()` with a proper SQL COUNT query using `select(func.count())`
2. Import `func` from sqlalchemy
3. Ensure the count query:
   - Filters by user_id
   - Respects the optional `completed` filter
4. Use `session.exec(count_query).one()` to return an integer
5. Do NOT load all rows into memory
6. Do NOT change API contracts or response shapes
7. Do NOT touch frontend code
8. Keep database schema unchanged
9. Ensure this fix prevents backend crashes so CORS headers are returned normally

Acceptance Criteria:
- GET /api/tasks returns 200 OK
- No AttributeError in logs
- No fake CORS errors in browser
- total_count returns correct integer
```

## Response Text

Successfully fixed the SQLModel count bug in the task CRUD skill. The issue was that in SQLAlchemy 2.x, `session.exec(query)` returns a `ScalarResult` object which does not support the `.count()` method that existed in older versions.

Key changes made:

1. **Added proper import**: Added `from sqlalchemy import func` to the imports in `backend/src/skills/task_crud_skill.py`

2. **Fixed the get_task_count_for_user method**:
   - Replaced the incorrect `session.exec(query).count()` with a proper SQL COUNT query using `select(func.count())`
   - Used `select(func.count()).select_from(Task).where(Task.user_id == user_id)` for the base query
   - Maintained the optional `completed` filter functionality
   - Used `session.exec(count_query).one()` to return the integer count value

3. **Maintained all constraints**:
   - Did not change API contracts or response shapes
   - Did not modify frontend code
   - Kept database schema unchanged
   - Ensured efficient query that doesn't load all rows into memory

The fix ensures that:
- GET /api/tasks will now return 200 OK instead of 500 errors
- No more AttributeError about 'ScalarResult' object not having 'count' attribute
- The total_count field returns the correct integer value
- CORS headers are properly returned since the backend no longer crashes

## Files Modified

- backend/src/skills/task_crud_skill.py

## Outcome

- Fixed the AttributeError causing 500 errors in GET /api/tasks
- Proper SQL COUNT query implemented using func.count()
- Optional completed filter functionality preserved
- Efficient counting without loading all records into memory
- Backend stability improved, preventing crashes that caused CORS issues

## Evaluation

The implementation successfully addresses all requirements:
- ✅ Replaced .count() with proper SQL COUNT query using func.count()
- ✅ Imported func from sqlalchemy
- ✅ Count query filters by user_id and respects completed filter
- ✅ Uses session.exec(count_query).one() to return integer
- ✅ Does not load all rows into memory
- ✅ No changes to API contracts or response shapes
- ✅ No frontend code touched
- ✅ Database schema unchanged
- ✅ Prevents backend crashes so CORS headers return normally