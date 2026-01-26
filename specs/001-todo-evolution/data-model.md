# Data Model: Evolution of Todo

## Entity Definitions

### User
- **id**: string (UUID) - Unique identifier for the user
- **email**: string - User's email address (unique, validated)
- **name**: string - User's display name (1-100 characters)
- **created_at**: datetime - Timestamp when user account was created
- **relationships**:
  - tasks (one-to-many) - User owns multiple tasks
  - conversations (one-to-many) - User has multiple chat conversations

### Task
- **id**: string (UUID) - Unique identifier for the task
- **user_id**: string (foreign key) - Reference to the owning user
- **title**: string - Task title (1-200 characters, required)
- **description**: string - Task description (0-1000 characters, optional)
- **completed**: boolean - Whether the task is completed (default: false)
- **created_at**: datetime - Timestamp when task was created
- **updated_at**: datetime - Timestamp when task was last modified
- **priority**: string (Phase V) - Task priority level (enum: high, medium, low, optional)
- **tags**: string array (Phase V) - Array of tags for the task (max 5, optional)
- **due_date**: datetime (Phase V) - When the task is due (optional)
- **recurrence**: string (Phase V) - Recurrence pattern (enum: daily, weekly, monthly, etc.)

### Conversation
- **id**: string (UUID) - Unique identifier for the conversation
- **user_id**: string (foreign key) - Reference to the owning user
- **created_at**: datetime - Timestamp when conversation was started
- **updated_at**: datetime - Timestamp when conversation was last updated
- **relationships**:
  - messages (one-to-many) - Conversation contains multiple messages

### Message
- **id**: string (UUID) - Unique identifier for the message
- **conversation_id**: string (foreign key) - Reference to the conversation
- **role**: string - Sender role (enum: user, assistant)
- **content**: string - Message content
- **created_at**: datetime - Timestamp when message was created

### RecurringPattern
- **id**: string (UUID) - Unique identifier for the pattern
- **frequency**: string - How often the task recurs (enum: daily, weekly, monthly, yearly)
- **interval**: integer - Interval multiplier (e.g., every 2 weeks)
- **ends_on**: datetime - When the recurrence ends (optional)
- **occurrences**: integer - How many times to repeat (optional, overrides ends_on)

## Validation Rules

### User Validation
- Email must be a valid email format
- Name must be 1-100 characters
- Email must be unique across all users

### Task Validation
- Title must be 1-200 characters
- Description must be 0-1000 characters
- Priority must be one of: high, medium, low (if provided)
- Tags array must contain maximum 5 elements
- Due date must be in the future (if provided)
- User_id must reference an existing user

### Message Validation
- Role must be either "user" or "assistant"
- Content must be 1-10000 characters
- Conversation_id must reference an existing conversation

## State Transitions

### Task State Transitions
- **Incomplete** → **Complete**: When user marks task as complete
- **Complete** → **Incomplete**: When user marks task as incomplete
- **Any state** → **Deleted**: When user deletes task (permanent deletion)

### User Authentication States
- **Unauthenticated** → **Authenticated**: When user logs in successfully
- **Authenticated** → **Unauthenticated**: When user logs out or session expires

## Relationships

- **User** (1) ←→ (Many) **Task**: User owns multiple tasks
- **User** (1) ←→ (Many) **Conversation**: User has multiple conversations
- **Conversation** (1) ←→ (Many) **Message**: Conversation contains multiple messages
- **Task** (1) ←→ (1) **RecurringPattern**: Task may have one recurrence pattern