# Feature Specification: Multi-User Web Application

**Feature Branch**: `001-multi-user-web-app`
**Created**: 2026-01-20
**Status**: Draft
**Input**: User description: "Phase 2 Specification — Full-Stack Multi-User Web App

Status: Phase 2 Only
Applies To: /backend, /frontend, shared monorepo concerns
Derived From: Phase 1 Implementation, Constitution, Plan
Workflow: Constitution → Specify → Plan → Tasks → Implement

1. Phase 2 Goal and Scope
1.1 Objective

Transform the Phase 1 single-user, in-memory console Todo app into a multi-user, full-stack web application with persistent storage, authentication, and strict user isolation.

Phase 2 introduces:

Web UI (browser-based)

REST API backend

Authentication and authorization

Persistent database storage

This phase does not include AI features, background jobs, cloud deployment, or Kubernetes. Those belong to later phases.

1.2 In Scope

Multi-user Todo management

RESTful backend API

Responsive frontend UI

JWT-based authentication

PostgreSQL persistence

Local development via Docker Compose

1.3 Out of Scope

AI agents or chatbot

Cloud deployment (production infra)

Role-based access control beyond basic users

External SaaS integrations beyond Neon Postgres

Offline-first or mobile apps

2. Guiding Principles (From Constitution)

Spec-driven development only
No manual coding. All code must be generated via Claude Code.
[From Constitution §1.1]

AI-native & reusable intelligence
Design logic as reusable skills/subagents where possible.
[From Constitution §1.3]

Security by default
Authentication required for all task operations.
[From Constitution §2.1]

Token efficiency
Clear, modular specs. No duplication across phases.
[From Constitution §1.4]

Cloud-native mindset
Even local development should mirror production patterns.
[From Constitution §3.1]

3. User Journeys (WHAT the system enables)
3.1 New User Registration

User opens the web app

User signs up with name, email, password

Account is created in the database

JWT access token is issued

User is redirected to their Todo dashboard

Acceptance Criteria

Email must be unique

Password is never stored in plain text

JWT is returned on successful signup

3.2 Existing User Login

User opens the app

User logs in with email and password

Backend validates credentials

JWT token is issued

User sees only their own tasks

3.3 Manage Todos (Core Features)

For an authenticated user:

Add a task

View list of tasks

Update task title/description

Mark task complete/incomplete

Delete a task

Acceptance Criteria

Tasks persist across sessions

Tasks are scoped strictly to the logged-in user

Unauthorized access is rejected

4. Functional Requirements
4.1 Authentication

Implement JWT-based auth using Better Auth

Tokens signed with a shared secret

Token required for all task-related endpoints

Rules

No anonymous access

Token validation via FastAPI middleware

Token contains user_id

4.2 Backend API (FastAPI)
Base Path

/api

Auth Endpoints

POST /api/auth/signup

POST /api/auth/login

Task Endpoints (Authenticated)

GET /api/{user_id}/tasks

POST /api/{user_id}/tasks

PUT /api/{user_id}/tasks/{task_id}

DELETE /api/{user_id}/tasks/{task_id}

PATCH /api/{user_id}/tasks/{task_id}/complete

Rules

user_id in path must match JWT user_id

Otherwise return 403 Forbidden

4.3 Frontend (Next.js)

App Router architecture

Pages:

/login

/signup

/dashboard

Responsive UI using Tailwind CSS

Uses fetch with Authorization headers

JWT stored securely (httpOnly cookie preferred)

5. Data Model & Persistence
5.1 Database

Neon Serverless PostgreSQL

SQLModel ORM

5.2 Schema
users
Field    Type    Notes
id    UUID    Primary key
email    string    Unique
name    string    Required
password_hash    string    Secure hash
created_at    timestamp    Auto
tasks
Field    Type    Notes
id    UUID    Primary key
user_id    UUID    FK → users.id
title    string    Required
description    string    Optional
completed    boolean    Default false
created_at    timestamp    Auto
updated_at    timestamp    Auto
6. Non-Functional Requirements
6.1 Security

Password hashing (industry standard)

JWT expiration

User isolation enforced at API level

No secrets committed to repo

6.2 Performance

Suitable for local development

Async FastAPI routes

Connection pooling via Neon

6.3 Maintainability

Clear separation of frontend and backend

Modular backend structure

Reusable agent skills (auth, DB access)

7. Monorepo Structure (Phase 2)
hackathon-todo/
├── backend/
│   ├── src/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── app/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── CLAUDE.md
├── AGENTS.md
├── phase1/
└── specs/

8. Dependency Constraints

Use UV for Python dependency management

Update pyproject.toml via uv add <package>

Use stable versions only (as of Jan 20, 2026)

Indicative versions:

FastAPI 0.104.1

SQLModel 0.0.8

Python 3.13+

Next.js 16+

Tailwind CSS stable

cmd2 remains Phase 1 only

9. Reusable Intelligence (AI-Native Design)

Phase 2 must prepare for reusable skills:

Suggested subagents:

auth_skill — signup/login/JWT logic

db_skill — database session and CRUD

user_isolation_skill — enforce user ownership

task_crud_skill — shared task operations

These are logical separations to support later phases.
[From Constitution §1.3]

10. Development & Execution Rules

Claude Code generates all code

No manual edits

Specs are the source of truth

Clean up duplicate virtual environments only if they cause issues

Keep the correct, required one

Use Docker Compose for local run

Prepare for MCP connections in later phases (do not implement yet)

11. Acceptance Checklist (Phase 2 Complete When)

Users can sign up and log in

JWT-based auth enforced everywhere

Tasks persist in PostgreSQL

Users only see their own tasks

Frontend and backend run via Docker Compose

Specs → Plan → Tasks → Implement flow followed exactly"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New User Registration (Priority: P1)

A new user visits the web application and wants to create an account so they can start managing their personal todo list. The user provides their name, email, and password, and receives an authenticated session upon successful registration.

**Why this priority**: This is the foundational user journey that enables all other functionality - without the ability to register, no other features can be used.

**Independent Test**: Can be fully tested by registering a new user with valid credentials and verifying that an account is created in the database and the user receives authentication tokens. Delivers the core value of allowing new users to join the platform.

**Acceptance Scenarios**:

1. **Given** a visitor accesses the web app, **When** they submit valid registration details (name, unique email, secure password), **Then** their account is created and they receive authentication tokens
2. **Given** a visitor attempts to register with an email that already exists, **When** they submit the registration form, **Then** they receive an error message indicating the email is already taken

---

### User Story 2 - Existing User Login (Priority: P1)

An existing user wants to access their todo list by logging into the application. They provide their email and password, and upon successful authentication, they can see only their own tasks.

**Why this priority**: Critical for user retention and ongoing use of the application - users need to access their existing data.

**Independent Test**: Can be tested by logging in with valid credentials and verifying that the user can access their dashboard and see only their own tasks.

**Acceptance Scenarios**:

1. **Given** a registered user enters valid login credentials, **When** they submit the login form, **Then** they are authenticated and redirected to their dashboard
2. **Given** a user enters invalid login credentials, **When** they submit the login form, **Then** they receive an appropriate error message and remain unauthenticated

---

### User Story 3 - Manage Personal Todo Tasks (Priority: P1)

An authenticated user wants to manage their personal todo tasks by adding, viewing, updating, and deleting items. They can mark tasks as complete or incomplete and all tasks are isolated to their account.

**Why this priority**: This is the core functionality that provides value to users - managing their tasks in a personalized way.

**Independent Test**: Can be tested by having an authenticated user perform CRUD operations on tasks and verifying that tasks are properly isolated to their account.

**Acceptance Scenarios**:

1. **Given** an authenticated user is on their dashboard, **When** they add a new task, **Then** the task is saved to their account and appears in their task list
2. **Given** an authenticated user has existing tasks, **When** they mark a task as complete, **Then** the task status is updated and persists across sessions
3. **Given** an authenticated user has tasks, **When** they delete a task, **Then** the task is removed from their account only
4. **Given** multiple authenticated users exist, **When** they access their dashboards, **Then** each user only sees their own tasks

---

### Edge Cases

- What happens when a user attempts to access another user's tasks via direct URL manipulation? The system should return a 403 Forbidden error.
- How does the system handle expired JWT tokens? The user should be redirected to the login page.
- What happens when a user attempts to register with invalid email format? The system should reject the input with a validation error.
- How does the system handle database connection failures during authentication? The system should gracefully handle the error and inform the user appropriately.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to register with name, email, and password
- **FR-002**: System MUST validate that email addresses are unique during registration
- **FR-003**: System MUST securely hash passwords before storing them
- **FR-004**: System MUST authenticate users via JWT tokens using Better Auth
- **FR-005**: System MUST restrict users to viewing only their own tasks
- **FR-006**: System MUST allow authenticated users to create, read, update, and delete their own tasks
- **FR-007**: System MUST persist user data in PostgreSQL database
- **FR-008**: System MUST validate JWT tokens for all task-related API endpoints
- **FR-009**: System MUST return 403 Forbidden when user attempts to access another user's resources
- **FR-010**: System MUST provide a responsive web UI with login, signup, and dashboard pages
- **FR-011**: System MUST store JWT tokens securely (preferably as httpOnly cookies)
- **FR-012**: System MUST allow users to mark tasks as complete/incomplete
- **FR-013**: System MUST validate user_id in API path matches the JWT user_id
- **FR-014**: System MUST log authentication events for security monitoring
- **FR-015**: System MUST handle database connection pooling for efficient resource usage

### Key Entities

- **User**: Represents a registered user account with unique email, name, password hash, and timestamps
- **Task**: Represents a todo item owned by a specific user with title, description, completion status, and timestamps
- **Authentication Token**: Represents a JWT that contains user identity information and has an expiration time

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete account registration in under 30 seconds
- **SC-002**: Users can log in and access their dashboard within 5 seconds
- **SC-003**: 100% of users can only see their own tasks, with zero cross-account data leakage
- **SC-004**: System maintains 99.9% uptime during local development testing
- **SC-005**: Task CRUD operations complete within 2 seconds under normal load
- **SC-006**: All authentication and authorization requirements are enforced without exceptions
- **SC-007**: Database operations succeed 99.5% of the time during normal operation
- **SC-008**: The application can be successfully deployed and run using Docker Compose
