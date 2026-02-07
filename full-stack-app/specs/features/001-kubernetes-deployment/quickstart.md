# Quickstart Guide: Kubernetes Deployment

## Prerequisites

- Docker Desktop v4.53+ with Gordon AI enabled
- Minikube (latest stable)
- Helm 3.x
- kubectl
- kubectl-ai plugin
- Kagent

## Environment Setup

### 1. Install and Enable Gordon (Docker AI)
```bash
# Install Docker Desktop v4.53+ and enable Gordon via Settings → Beta features → Toggle on
docker ai "What can you do?"
```

### 2. Install Minikube
```bash
# Install minikube (follow official installation guide for your OS)
minikube start --driver=docker
```

### 3. Install Helm
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 4. Install kubectl-ai and Kagent
```bash
# On macOS
brew install kubectl-ai kagent

# On Linux (alternative methods)
# Follow the official installation guides for your distribution
```

## Containerization

### 1. Build Frontend Container
```bash
# Using Docker AI Agent (Gordon)
docker ai "build frontend container from ./frontend"

# Or manually if Docker AI unavailable
cd frontend
docker build -t todo-frontend:latest .
```

### 2. Build Backend Container
```bash
# Using Docker AI Agent (Gordon)
docker ai "build backend container from ./backend"

# Or manually if Docker AI unavailable
cd backend
docker build -t todo-backend:latest .
```

## Helm Chart Creation

### 1. Create Frontend Helm Chart
```bash
mkdir -p helm/frontend
cd helm/frontend
helm create frontend
```

### 2. Create Backend Helm Chart
```bash
mkdir -p helm/backend
cd helm/backend
helm create backend
```

## Kubernetes Deployment

### 1. Deploy Backend Service
```bash
helm install todo-backend ./helm/backend \
  --set image.repository=todo-backend \
  --set image.tag=latest \
  --set service.type=NodePort \
  --set service.port=8000
```

### 2. Deploy Frontend Service
```bash
helm install todo-frontend ./helm/frontend \
  --set image.repository=todo-frontend \
  --set image.tag=latest \
  --set service.type=NodePort \
  --set service.port=3000
```

## Verification

### 1. Check Deployments
```bash
kubectl-ai "get deployments"
kubectl-ai "get pods"
kubectl-ai "get services"
```

### 2. Scale Services
```bash
kubectl-ai "scale deployment todo-frontend --replicas=2"
kubectl-ai "scale deployment todo-backend --replicas=2"
```

### 3. Analyze Cluster Health
```bash
kagent "analyze cluster health"
```

## Accessing the Application

### 1. Get Service Endpoints
```bash
minikube service todo-frontend --url
minikube service todo-backend --url
```

### 2. Open Browser
```bash
minikube service todo-frontend
```

## Troubleshooting

### 1. Check Pod Logs
```bash
kubectl-ai "get pods"
kagent "collect logs from todo-frontend and todo-backend"
```

### 2. Diagnose Issues
```bash
kubectl-ai "describe pod <pod-name>"
kubectl-ai "check pod failures"
```

## Cleanup

### 1. Uninstall Helm Releases
```bash
helm uninstall todo-frontend
helm uninstall todo-backend
```

### 2. Stop Minikube
```bash
minikube stop
```