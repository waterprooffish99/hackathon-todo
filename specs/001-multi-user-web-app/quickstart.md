# Quickstart Guide: Multi-User Web Application

**Feature**: 001-multi-user-web-app
**Date**: 2026-01-20

## Overview

This guide provides a quick overview of how to set up and run the multi-user web application locally. The system consists of a Next.js frontend, FastAPI backend, and PostgreSQL database.

## URLs & Ports

- **Frontend URL**: http://localhost:3000
- **Backend API URL**: http://localhost:8000
- **Database**: postgresql://localhost:5432/tododb

## Prerequisites

- Python 3.13+
- Node.js 18+ (for frontend)
- Docker and Docker Compose
- UV package manager
- Git

## Local Development Setup

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd hackathon-todo
```

### 2. Environment Setup

Copy the example environment file and customize as needed:
```bash
cp .env.example .env
# Edit .env with your specific values
```

### 3. Backend Setup

#### Install Python Dependencies
```bash
cd backend
uv venv  # Create virtual environment
source .venv/bin/activate  # Activate virtual environment
uv pip install -r requirements.txt
# Or add dependencies individually:
# uv add fastapi sqlmodel python-jose[cryptography] passlib[bcrypt] python-multipart
```

#### Run Backend (Development)
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the development server
uv run python -m src.main

# Or with Uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup

#### Install Node Dependencies
```bash
cd frontend
npm install
# or
yarn install
```

#### Run Frontend (Development)
```bash
npm run dev
# or
yarn dev
```

### 5. Run with Docker Compose (Recommended)

Run the entire stack:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT

### Tasks
- `GET /api/{user_id}/tasks` - Get user's tasks
- `POST /api/{user_id}/tasks` - Create new task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle completion

## Test Credentials Example

For testing purposes, you can use the following patterns:
- Email: testuser@example.com, user2@example.com
- Password: TestPass123!
- Name: Test User

## Phase 3 Readiness

Application is ready for Phase 3 development:
- ✅ Full authentication system implemented
- ✅ User isolation enforced
- ✅ Task CRUD operations complete
- ✅ Docker Compose configuration ready
- ✅ Frontend and backend properly integrated
- ✅ End-to-end flows verified

## Folder Structure

```
hackathon-todo/
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   └── tasks.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── task.py
│   │   ├── skills/
│   │   │   ├── auth_skill.py
│   │   │   ├── db_skill.py
│   │   │   ├── user_isolation_skill.py
│   │   │   └── task_crud_skill.py
│   │   └── middleware/
│   │       └── auth.py
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── login/
│   │   ├── signup/
│   │   └── dashboard/
│   ├── lib/
│   │   └── api.ts
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── specs/
    └── 001-multi-user-web-app/
```

## Running Tests

### Backend Tests
```bash
# With virtual environment activated
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
# or
npm run test:watch
```

## Development Commands

### Backend Development
```bash
# Run with auto-reload
uvicorn src.main:app --reload

# Format code
black src/
# or
ruff format src/

# Lint code
ruff check src/

# Run migrations
alembic upgrade head
```

### Frontend Development
```bash
# Development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Format code
npm run format
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in environment variables
   - Ensure network connectivity between services

2. **JWT Authentication Issues**
   - Verify SECRET_KEY matches between frontend and backend
   - Check token expiration times
   - Ensure proper Authorization header format

3. **CORS Issues**
   - Verify frontend origin is allowed in backend settings
   - Check backend is configured to accept credentials

4. **Dependency Issues**
   - Use UV for Python dependencies
   - Ensure Python 3.13+ is installed
   - Clear cache if needed: `uv cache clean`

## Next Steps

1. Implement the skills architecture as planned
2. Set up proper error handling
3. Add input validation
4. Implement comprehensive tests
5. Set up CI/CD pipeline