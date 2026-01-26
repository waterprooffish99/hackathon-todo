# Quickstart Guide: Evolution of Todo

## Phase I: Python Console App

### Setup
1. Install Python 3.13+ and UV
2. Clone the repository
3. Navigate to the project root
4. Run `uv sync` to install dependencies
5. Run `python src/main.py` to start the CLI app

### Basic Commands
- `add "task title" "optional description"` - Create a new task
- `list` - View all tasks
- `complete <task_id>` - Mark a task as complete
- `update <task_id> "new title" "new description"` - Update task details
- `delete <task_id>` - Remove a task

## Phase II: Full-Stack Web Application

### Backend Setup
1. Set up Neon PostgreSQL database
2. Configure Better Auth credentials
3. Run `cd backend && uv sync`
4. Run migrations: `python -m alembic upgrade head`
5. Start server: `fastapi dev`

### Frontend Setup
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Configure environment variables for backend API and auth
4. Start development server: `npm run dev`

### Environment Variables
```bash
# Backend
DATABASE_URL=your_neon_db_url
JWT_SECRET=your_jwt_secret
BETTER_AUTH_SECRET=your_auth_secret

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

## Phase III: AI-Powered Chatbot

### Setup
1. Obtain OpenAI API key
2. Set up MCP server with task management tools
3. Configure chat endpoint in backend
4. Enable ChatKit in frontend with proper domain allowlisting

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_key
MCP_SERVER_URL=your_mcp_server_url
```

## Phase IV: Kubernetes Deployment

### Prerequisites
- Docker installed
- Minikube running
- Helm installed

### Deployment Steps
1. Build Docker images: `docker build -t todo-app .`
2. Package Helm charts: `helm package k8s/`
3. Install with Helm: `helm install todo-app todo-app-*.tgz`

## Phase V: Advanced Cloud Deployment

### Prerequisites
- Kafka/Redpanda cluster
- Dapr installed on cluster
- DigitalOcean Kubernetes cluster

### Setup
1. Deploy Dapr components: `kubectl apply -f dapr-components/`
2. Deploy Kafka topics using Strimzi or Redpanda Cloud
3. Deploy services with Dapr sidecars
4. Configure CI/CD pipeline for automated deployments