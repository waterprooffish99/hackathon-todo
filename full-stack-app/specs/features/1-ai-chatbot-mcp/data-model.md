# Data Model: AI-Powered Conversational Todo Chatbot

## Core Entities

### Task
Represents a user's Todo item with associated metadata.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the task
- `user_id`: UUID (Foreign Key) - Reference to the owning user
- `title`: String (Required, max 255 chars) - Brief description of the task
- `description`: String (Optional, max 1000 chars) - Detailed notes about the task
- `completed`: Boolean (Default: false) - Completion status of the task
- `created_at`: DateTime (Auto-generated) - Timestamp when task was created
- `updated_at`: DateTime (Auto-generated) - Timestamp when task was last updated

**Relationships**:
- Belongs to one User (Many-to-One)
- Part of one Conversation (Many-to-Many through association)

**Validation Rules**:
- Title must not be empty
- User ID must reference an existing user
- Cannot modify completed status without proper authorization

### User
Identity for data isolation with authentication credentials.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the user
- `username`: String (Unique, Required, max 100 chars) - User's login identifier
- `email`: String (Unique, Required, max 255 chars) - User's email address
- `password_hash`: String (Required) - Securely hashed password
- `created_at`: DateTime (Auto-generated) - Account creation timestamp
- `updated_at`: DateTime (Auto-generated) - Last modification timestamp

**Relationships**:
- Has many Tasks (One-to-Many)
- Has many Conversations (One-to-Many)
- Has many Messages (One-to-Many)

**Validation Rules**:
- Username must be unique
- Email must be valid format and unique
- Password must meet security requirements

### Conversation
Represents a session of interaction between user and AI assistant.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the conversation
- `user_id`: UUID (Foreign Key) - Reference to the owning user
- `title`: String (Optional, max 255 chars) - Auto-generated or user-defined title
- `started_at`: DateTime (Auto-generated) - When the conversation began
- `last_activity_at`: DateTime (Auto-generated) - When last message was sent
- `is_active`: Boolean (Default: true) - Whether conversation is ongoing

**Relationships**:
- Belongs to one User (Many-to-One)
- Has many Messages (One-to-Many)
- Associated with many Tasks (Many-to-Many through association)

**Validation Rules**:
- User ID must reference an existing user
- Cannot have multiple active conversations per user simultaneously

### Message
Individual communication in a conversation with role-based context.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the message
- `conversation_id`: UUID (Foreign Key) - Reference to the parent conversation
- `role`: Enum ('user'|'assistant'|'system') - Defines the sender type
- `content`: Text (Required) - The actual message content
- `timestamp`: DateTime (Auto-generated) - When the message was created
- `tool_calls`: JSON (Optional) - Details of any tools called by this message
- `tool_responses`: JSON (Optional) - Responses from tools called

**Relationships**:
- Belongs to one Conversation (Many-to-One)
- May reference specific Tasks (Many-to-Many through association)

**Validation Rules**:
- Conversation ID must reference an existing conversation
- Role must be one of the allowed values
- Content must not be empty

## State Transitions

### Task States
- `pending` → `completed`: When task is marked as done
- `completed` → `pending`: When task is marked as incomplete
- `pending` → `archived`: When task is moved to archive
- `completed` → `archived`: When completed task is archived

### Conversation States
- `initiated` → `active`: When first user message is received
- `active` → `paused`: When conversation is temporarily inactive
- `paused` → `active`: When user resumes conversation
- `active` → `closed`: When conversation is concluded
- `paused` → `closed`: When paused conversation is closed

## Relationships

```
User (1) ────── (Many) Task
   │                   │
   │                   │
   │ (1) ────── (Many) │
   ▼                   ▼
Conversation ────── Message
   (1)    ────── (Many)
```

## Indexes

### Primary Indexes
- `tasks.id` - B-tree index (primary key)
- `users.id` - B-tree index (primary key)
- `conversations.id` - B-tree index (primary key)
- `messages.id` - B-tree index (primary key)

### Foreign Key Indexes
- `tasks.user_id` - B-tree index
- `conversations.user_id` - B-tree index
- `messages.conversation_id` - B-tree index

### Query Optimization Indexes
- `tasks.completed` - B-tree index (for filtering by completion status)
- `conversations.last_activity_at` - B-tree index (for sorting by recency)
- `messages.timestamp` - B-tree index (for chronological ordering)
- `users.username` - B-tree index (for authentication lookups)
- `users.email` - B-tree index (for authentication lookups)

## Constraints

### Data Integrity
- Foreign key constraints to ensure referential integrity
- NOT NULL constraints on required fields
- Unique constraints on username and email fields
- Check constraints for enum values (role field in messages)

### Business Logic
- Tasks can only be modified by their owner
- Messages cannot be modified after creation
- Users cannot have multiple active conversations simultaneously
- Task completion can only be toggled by the task owner