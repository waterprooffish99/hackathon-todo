# Quickstart Guide: Cloud-Native AI Todo Platform - Phase V

## Prerequisites

- Python 3.13+
- UV package manager
- Docker and Docker Compose
- Minikube or access to Kubernetes cluster
- Dapr CLI
- kubectl

## Setup

### 1. Clone and Initialize
```bash
git clone <repo-url>
cd hackathon-todo
uv venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
# Backend services
cd backend/main-api
uv pip install -r requirements.txt

cd ../recurring-task-service
uv pip install -r requirements.txt

cd ../notification-service
uv pip install -r requirements.txt

cd ../audit-service
uv pip install -r requirements.txt
```

### 3. Start Local Development Environment
```bash
# Start Minikube
minikube start

# Install Dapr
dapr init -k

# Deploy Kafka (using Strimzi)
kubectl apply -f infrastructure/kafka-config/

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app=strimzi-kafka --timeout=300s

# Deploy services with Helm
helm install todo-platform infrastructure/helm-charts/todo-platform/
```

### 4. Configure Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Update with your specific values
# - Database connection details
# - Dapr component configurations
# - External service endpoints
```

## Running the Services

### Development Mode
```bash
# Run main API service locally with Dapr
dapr run --app-id main-api --app-port 8000 --dapr-http-port 3500 -- uvicorn src.main:app --reload

# Run other services similarly
dapr run --app-id recurring-task-service --app-port 8001 --dapr-http-port 3501 -- uvicorn src.main:app --reload
dapr run --app-id notification-service --app-port 8002 --dapr-http-port 3502 -- uvicorn src.main:app --reload
dapr run --app-id audit-service --app-port 8003 --dapr-http-port 3503 -- uvicorn src.main:app --reload
```

### Production Mode (Kubernetes)
```bash
# Deploy to Kubernetes
helm upgrade --install todo-platform infrastructure/helm-charts/todo-platform/ --values infrastructure/helm-charts/todo-platform/values.yaml

# Verify deployment
kubectl get pods
kubectl get services
kubectl get daprapps
```

## Key Components

### Main API Service
- Entry point for all API requests
- Orchestrates AI subagents
- Handles user authentication
- Available at http://localhost:3000 (or your ingress URL)

### AI Subagents
- Task Interpretation Agent: Processes natural language task descriptions
- Scheduling Intelligence Agent: Determines optimal due dates and reminders
- Reminder Reasoning Agent: Calculates and manages reminder timing

### Event-Driven Services
- Recurring Task Service: Consumes task completion events to create next occurrences
- Notification Service: Consumes reminder events to send user notifications
- Audit Service: Consumes all task events for immutable logging

## Testing

### Unit Tests
```bash
# Run tests for main API
cd backend/main-api
python -m pytest tests/unit/

# Run tests for other services
cd backend/recurring-task-service
python -m pytest tests/unit/
```

### Integration Tests
```bash
# Run integration tests
cd backend/main-api
python -m pytest tests/integration/
```

### Contract Tests
```bash
# Run API contract tests
cd backend/main-api
python -m pytest tests/contract/
```

## Monitoring

### Dapr Dashboard
```bash
dapr dashboard
```

### Service Logs
```bash
# View logs for all services
kubectl logs -l app=main-api
kubectl logs -l app=recurring-task-service
kubectl logs -l app=notification-service
kubectl logs -l app=audit-service
```

### Health Checks
- Main API: GET /health
- Dapr Sidecar: GET http://localhost:3501/v1.0/healthz
- All services expose metrics at /metrics