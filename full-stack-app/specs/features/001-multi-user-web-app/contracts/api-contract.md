# API Contract: Multi-User Web Application

**Feature**: 001-multi-user-web-app
**Date**: 2026-01-20
**Version**: 1.0

## Overview

This document defines the REST API contract for the multi-user web application. The API follows RESTful principles with user isolation enforced through JWT tokens and path-based user identification.

## Base URL

```
/api
```

## Authentication

All API endpoints (except auth endpoints) require JWT authentication via Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Common Headers

### Request Headers
- `Authorization: Bearer <jwt_token>` (for protected endpoints)
- `Content-Type: application/json` (for POST/PUT/PATCH requests)

### Response Headers
- `Content-Type: application/json`
- `X-Request-ID: <uuid>` (for request tracing)

## Error Responses

All error responses follow the same structure:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-01-20T10:00:00Z"
}
```

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `422`: Unprocessable Entity
- `500`: Internal Server Error

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/signup

Register a new user account.

**Request Body**:
```json
{
  "name": "string (required, min 1 char)",
  "email": "string (required, valid email format)",
  "password": "string (required, secure password)"
}
```

**Success Response (201)**:
```json
{
  "user_id": "uuid",
  "email": "string",
  "name": "string",
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

**Error Responses**:
- `400`: Invalid input format
- `409`: Email already exists
- `422`: Validation error

#### POST /api/auth/login

Authenticate user and return JWT token.

**Request Body**:
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Success Response (200)**:
```json
{
  "user_id": "uuid",
  "email": "string",
  "name": "string",
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

**Error Responses**:
- `400`: Invalid input format
- `401`: Invalid credentials
- `422`: Validation error

### Task Management Endpoints

All task endpoints require authentication and enforce user isolation.

#### GET /api/{user_id}/tasks

Retrieve all tasks for a specific user.

**Path Parameters**:
- `user_id`: UUID (required, must match JWT user_id)

**Query Parameters**:
- `completed`: boolean (optional, filter by completion status)
- `limit`: integer (optional, pagination limit, default 50)
- `offset`: integer (optional, pagination offset, default 0)

**Success Response (200)**:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "string",
      "description": "string or null",
      "completed": false,
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-20T10:00:00Z"
    }
  ],
  "total_count": 10,
  "page": 1,
  "limit": 50
}
```

**Error Responses**:
- `401`: Unauthorized
- `403`: User ID mismatch (path user_id ≠ JWT user_id)
- `404`: User not found
- `422`: Invalid query parameters

#### POST /api/{user_id}/tasks

Create a new task for a user.

**Path Parameters**:
- `user_id`: UUID (required, must match JWT user_id)

**Request Body**:
```json
{
  "title": "string (required, min 1 char, max 255 char)",
  "description": "string (optional, max 1000 char)"
}
```

**Success Response (201)**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string or null",
  "completed": false,
  "created_at": "2026-01-20T10:00:00Z",
  "updated_at": "2026-01-20T10:00:00Z"
}
```

**Error Responses**:
- `400`: Invalid input format
- `401`: Unauthorized
- `403`: User ID mismatch (path user_id ≠ JWT user_id)
- `404`: User not found
- `422`: Validation error

#### PUT /api/{user_id}/tasks/{task_id}

Update an existing task.

**Path Parameters**:
- `user_id`: UUID (required, must match JWT user_id)
- `task_id`: UUID (required, task to update)

**Request Body**:
```json
{
  "title": "string (required, min 1 char, max 255 char)",
  "description": "string (optional, max 1000 char)"
}
```

**Success Response (200)**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string or null",
  "completed": false,
  "created_at": "2026-01-20T10:00:00Z",
  "updated_at": "2026-01-20T10:00:00Z"
}
```

**Error Responses**:
- `400`: Invalid input format
- `401`: Unauthorized
- `403`: User ID mismatch or task doesn't belong to user
- `404`: Task not found
- `422`: Validation error

#### DELETE /api/{user_id}/tasks/{task_id}

Delete a task.

**Path Parameters**:
- `user_id`: UUID (required, must match JWT user_id)
- `task_id`: UUID (required, task to delete)

**Success Response (204)**:
No content returned.

**Error Responses**:
- `401`: Unauthorized
- `403`: User ID mismatch or task doesn't belong to user
- `404`: Task not found

#### PATCH /api/{user_id}/tasks/{task_id}/complete

Toggle task completion status.

**Path Parameters**:
- `user_id`: UUID (required, must match JWT user_id)
- `task_id`: UUID (required, task to update)

**Request Body**:
```json
{
  "completed": "boolean (required)"
}
```

**Success Response (200)**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string or null",
  "completed": true,
  "created_at": "2026-01-20T10:00:00Z",
  "updated_at": "2026-01-20T10:00:00Z"
}
```

**Error Responses**:
- `400`: Invalid input format
- `401`: Unauthorized
- `403`: User ID mismatch or task doesn't belong to user
- `404`: Task not found
- `422`: Validation error

## Security Requirements

### JWT Token Validation
- All task endpoints require valid JWT in Authorization header
- JWT must not be expired
- user_id in URL path must match user_id in JWT payload
- Return 403 if user_id mismatch occurs

### User Isolation
- Users can only access their own tasks
- Cross-user data access must be prevented
- All queries must be filtered by user_id

### Input Validation
- All inputs must be validated for type, length, and format
- Sanitize inputs to prevent injection attacks
- Use proper ORM/ODM features to prevent injection

## Rate Limiting

### Recommended Limits
- Auth endpoints: 5 requests per minute per IP
- Task endpoints: 100 requests per minute per user
- Apply rate limiting at the API gateway or middleware level

## Versioning

- API version not currently implemented (assumed v1)
- Future versions should use header-based versioning: `API-Version: 1`
- Backward compatibility should be maintained where possible

## CORS Policy

- Allow requests from frontend domain only
- Support credentials in requests
- Limit allowed methods to required set

## Monitoring and Logging

### Required Logs
- Request/response for debugging
- Authentication attempts (success/failure)
- Rate limit violations
- Error responses with context

### Metrics
- Request rate per endpoint
- Response time percentiles
- Error rates by type
- Active users count