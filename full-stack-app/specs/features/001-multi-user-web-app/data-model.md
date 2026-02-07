# Data Model: Multi-User Web Application

**Feature**: 001-multi-user-web-app
**Date**: 2026-01-20
**Based on**: Feature specification and constitution

## Overview

This document defines the data models for the multi-user web application, including entity definitions, relationships, validation rules, and state transitions. The models are designed to support user isolation and authentication requirements.

## Entity Definitions

### User Entity

**Description**: Represents a registered user account with authentication credentials and metadata.

**Fields**:
- `id`: UUID (Primary Key)
  - Auto-generated UUID
  - Required, immutable
- `email`: String
  - User's email address
  - Required, unique across all users
  - Validated as email format
- `name`: String
  - User's display name
  - Required, min length 1 character
- `password_hash`: String
  - Securely hashed password
  - Required, stored as hash only
  - Never stored in plain text
- `created_at`: DateTime (Timestamp)
  - Account creation time
  - Auto-populated on creation
  - Immutable after creation

**Validation Rules**:
- Email must be unique across all users
- Email must match valid email format
- Name must be at least 1 character
- Password must be securely hashed before storage
- Email cannot be changed after account creation

**Relationships**:
- One-to-many relationship with Task entity (one user owns many tasks)

### Task Entity

**Description**: Represents a todo item owned by a specific user with status and metadata.

**Fields**:
- `id`: UUID (Primary Key)
  - Auto-generated UUID
  - Required, immutable
- `user_id`: UUID (Foreign Key)
  - Reference to owning user
  - Required, links to User.id
  - Immutable after creation
- `title`: String
  - Task title or subject
  - Required, min length 1 character
  - Max length 255 characters
- `description`: String (Optional)
  - Detailed task description
  - Optional, nullable
  - Max length 1000 characters
- `completed`: Boolean
  - Completion status
  - Required, defaults to False
  - Mutable (can change between True/False)
- `created_at`: DateTime (Timestamp)
  - Task creation time
  - Auto-populated on creation
  - Immutable after creation
- `updated_at`: DateTime (Timestamp)
  - Last modification time
  - Auto-updated on any change
  - Updated on creation and subsequent changes

**Validation Rules**:
- user_id must reference an existing User
- title must be at least 1 character
- title must not exceed 255 characters
- user_id cannot be changed after creation
- Only the owning user can modify this task
- Only the owning user can delete this task

**Relationships**:
- Many-to-one relationship with User entity (many tasks owned by one user)

### Authentication Token Entity (Conceptual)

**Description**: Represents JWT tokens for user authentication (managed by Better Auth).

**Fields**:
- `token`: String (JWT)
  - Encoded JWT containing user identity
  - Contains user_id, expiration time
- `user_id`: UUID
  - Associated user
  - Extracted from JWT payload
- `expires_at`: DateTime
  - Token expiration time
  - Determined by JWT claims

**Validation Rules**:
- Token must be valid JWT format
- Token must not be expired
- Token must contain valid user_id
- Token signature must be valid

## Entity Relationships

```
User (1) ←→ (Many) Task
  │              │
  │              │
  └─ owns ───────┘
```

- One User can own many Tasks
- Each Task belongs to exactly one User
- Tasks are isolated to their owner
- User deletion would cascade to their Tasks (future consideration)

## Business Rules

### User Isolation
- Users can only access their own tasks
- API endpoints must validate user_id in JWT matches requested resource
- Database queries must filter by user_id
- Cross-user data access is prohibited

### Data Integrity
- Foreign key constraints ensure referential integrity
- Required fields cannot be null
- Unique constraints prevent duplicates where appropriate
- Timestamps are auto-managed

### Privacy & Security
- Passwords are never stored in plain text
- Password hashes are stored securely
- User emails are unique identifiers
- Authentication tokens are validated for each request

## Access Patterns

### User-centric Queries
- Retrieve all tasks for a specific user
- Count tasks for a specific user
- Filter tasks by completion status for a specific user

### Task-centric Operations
- Create task for a specific user
- Update specific task owned by user
- Delete specific task owned by user
- Toggle completion status of specific task

## Indexing Strategy

### Recommended Database Indexes
- User.email (unique index for fast lookups)
- Task.user_id (index for user isolation queries)
- Task.user_id + Task.completed (composite index for filtered queries)
- Task.updated_at (index for sorting by recency)

## Constraints Summary

| Entity | Constraint | Enforcement |
|--------|------------|-------------|
| User | Email uniqueness | Database unique constraint |
| User | Email format | Application-level validation |
| Task | User ownership | Foreign key constraint + application validation |
| Task | Required fields | Database NOT NULL + application validation |
| Both | UUID primary keys | Database-generated UUIDs |
| Both | Automatic timestamps | ORM/database triggers |

## Future Considerations

### Potential Extensions
- Soft delete capability for tasks
- Task categories or tags
- Due dates and reminders
- Shared tasks between users (future phase)

### Performance Considerations
- Pagination for users with many tasks
- Caching strategies for frequent read operations
- Bulk operations for task management