# Data Model: Cloud-Native AI Todo Platform - Phase V

## Core Entities

### Task
Represents a user's to-do item with advanced features
- **task_id**: UUID (primary key)
- **title**: String (required, max 255 chars)
- **description**: Text (optional)
- **priority**: Enum ('low', 'medium', 'high') (default: 'medium')
- **tags**: Array of strings (free-form tags, max 10 tags, 50 chars each)
- **due_at**: DateTime (optional)
- **remind_at**: DateTime (optional)
- **completed**: Boolean (default: false)
- **completion_date**: DateTime (optional, set when completed)
- **recurrence_rule**: Enum ('daily', 'weekly', 'monthly', null) (optional)
- **user_id**: UUID (foreign key to User)
- **created_at**: DateTime (auto-generated)
- **updated_at**: DateTime (auto-generated)
- **version**: Integer (for optimistic locking)

### User
Represents an authenticated user
- **user_id**: UUID (primary key)
- **email**: String (unique, required)
- **name**: String (optional)
- **created_at**: DateTime (auto-generated)
- **updated_at**: DateTime (auto-generated)

### Event
Represents a system event for the event-driven architecture
- **event_id**: UUID (primary key)
- **event_type**: String (required, e.g., 'task.created', 'task.completed')
- **event_version**: String (semantic version, default: '1.0.0')
- **task_id**: UUID (foreign key to Task)
- **user_id**: UUID (foreign key to User)
- **payload**: JSON (full task payload)
- **timestamp**: DateTime (auto-generated)
- **correlation_id**: String (for tracing)
- **processed**: Boolean (for idempotency in consumers)

### AuditLog
Immutable record of task events for compliance and debugging
- **log_id**: UUID (primary key)
- **event_id**: UUID (foreign key to Event)
- **task_id**: UUID (foreign key to Task)
- **user_id**: UUID (foreign key to User)
- **action**: String (e.g., 'task_created', 'task_updated', 'task_completed', 'task_deleted')
- **previous_state**: JSON (previous task state, nullable)
- **new_state**: JSON (new task state)
- **timestamp**: DateTime (auto-generated)
- **metadata**: JSON (additional context)

## Relationships

- **User** (1) ←→ (Many) **Task**: One user can have many tasks
- **Task** (1) ←→ (Many) **Event**: One task can generate many events
- **Event** (1) ←→ (1) **AuditLog**: One event corresponds to one audit log entry

## Validation Rules

### Task Validation
- Title must be 1-255 characters
- Description must be ≤ 10000 characters
- Priority must be one of 'low', 'medium', 'high'
- Tags array must have ≤ 10 elements
- Each tag must be ≤ 50 characters
- Due date must be in the future if provided
- Remind date must be in the future and before due date if both provided
- Recurrence rule only applies if the task is completed and marked as recurring

### Event Validation
- Event type must follow format 'entity.action' (e.g., 'task.created')
- Event version must follow semantic versioning
- Payload must contain valid task data structure
- Correlation ID must be consistent across related events

### Audit Log Validation
- Action must be one of predefined values: 'task_created', 'task_updated', 'task_completed', 'task_deleted'
- New state must be a valid task object
- Previous state must be null for 'task_created' events

## State Transitions

### Task State Transitions
- `created` → `active` (when first created)
- `active` → `completed` (when user marks as done)
- `completed` → `active` (when user reopens)
- `active` → `deleted` (when user deletes)
- `completed` → `recurring` (when recurring task generates next occurrence)

### Event Processing States
- `published` → `processing` → `processed` (for idempotency)
- Events must be processed in order when possible
- Failed events should be retried with exponential backoff

## Indexes

### Task Table
- Primary: task_id
- Foreign key: user_id
- Composite: (user_id, completed, priority) for efficient filtering
- Composite: (user_id, due_at) for efficient due date queries
- Composite: (user_id, remind_at) for reminder processing

### Event Table
- Primary: event_id
- Foreign keys: task_id, user_id
- Index: timestamp for chronological processing
- Index: event_type for filtering by event kind
- Index: correlation_id for tracing

### AuditLog Table
- Primary: log_id
- Foreign keys: event_id, task_id, user_id
- Index: timestamp for chronological access
- Index: action for filtering by operation type