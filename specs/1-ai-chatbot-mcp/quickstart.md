# Quickstart Guide: AI-Powered Conversational Todo Chatbot

## Prerequisites

- Python 3.13+ with pip
- Node.js 18+ with npm
- PostgreSQL (or use provided Docker setup)
- OpenAI API key
- MCP-compatible client (for tool integration)

## Setup Instructions

### 1. Clone and Initialize Repository

```bash
git clone <repository-url>
cd hackathon-todo
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with UV (as per constitution)
uv pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your PostgreSQL connection string and OpenAI API key
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit NEXT_PUBLIC_API_BASE_URL to match your backend URL
```

### 4. Database Initialization

```bash
# From backend directory with activated virtual environment
python -c "from src.db.database import create_db_and_tables; create_db_and_tables()"
```

### 5. MCP Tool Configuration

```bash
# From backend directory
# Ensure MCP server is configured to expose Todo operations
# Check src/mcp/tools.py for tool definitions
```

## Running the Application

### Development Mode

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Start MCP server (optional, if running separately)
cd backend
python -c "from src.mcp.server import run_server; run_server()"  # Adjust path as needed
```

### Production Mode

```bash
# Build frontend
cd frontend
npm run build

# Start backend with production server
cd backend
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db
OPENAI_API_KEY=sk-your-openai-api-key
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MCP_SERVER_URL=http://localhost:8001
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_MCP_ENDPOINT=http://localhost:8001
```

## Initial Configuration

### 1. Create Admin User
```bash
# After starting the backend
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Admin User", "email": "admin@example.com", "password": "SecurePass123!"}'
```

### 2. Verify MCP Tools
- Navigate to `/tools` endpoint to see exposed MCP tools
- Verify `add_task`, `list_tasks`, `update_task`, `delete_task`, and `toggle_complete` are available

## API Endpoints

### Backend (http://localhost:8000)
- `GET /health` - Health check
- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - User registration
- `POST /api/chat` - Chat interface with AI agent
- `GET /tools` - MCP tools discovery

### Frontend (http://localhost:3000)
- `/` - Home/landing page
- `/chat` - Main chat interface
- `/login` - Login page
- `/signup` - Registration page

## First Steps

1. Visit http://localhost:3000 to access the chat interface
2. Register a new account or log in
3. Start chatting with the AI assistant using natural language:
   - "Add a task: Buy groceries with note: get milk and bread"
   - "Show my tasks"
   - "Mark task 1 as complete"
   - "Update task 'Buy groceries' to 'Buy groceries for weekend party'"
4. The AI agent will call MCP tools to perform requested operations

## Troubleshooting

### Common Issues

**Issue**: Database connection errors
**Solution**: Verify DATABASE_URL in backend/.env and ensure PostgreSQL is running

**Issue**: AI agent not responding
**Solution**: Check OPENAI_API_KEY in backend/.env and verify API connectivity

**Issue**: Frontend can't connect to backend
**Solution**: Verify NEXT_PUBLIC_API_BASE_URL in frontend/.env.local

**Issue**: MCP tools not available
**Solution**: Ensure MCP server is running and properly configured in backend

### Logs
- Backend: Check console output or configured logging
- Frontend: Check browser console and network tab
- Database: Check PostgreSQL logs if connection issues persist