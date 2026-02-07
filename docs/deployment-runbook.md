# Deployment Runbook: Cloud-Native AI Todo Platform

## Overview

This runbook provides instructions for deploying the Cloud-Native AI Todo Platform to various environments (Minikube for local, AKS/GKE/OCI for production).

## Prerequisites

### Local Development (Minikube)
- Docker and Docker Desktop
- Minikube
- kubectl
- Helm 3+
- Dapr CLI
- Python 3.13+
- UV package manager

### Production Deployment
- Access to Kubernetes cluster (AKS, GKE, or OCI)
- kubectl configured for cluster access
- Helm 3+
- Dapr installed in cluster
- Kafka/Strimzi installed in cluster

## Deployment Steps

### 1. Local Deployment (Minikube)

#### 1.1 Start Minikube
```bash
minikube start --cpus=4 --memory=8192 --disk-size=20g
minikube addons enable ingress
minikube addons enable metrics-server
```

#### 1.2 Install Dapr
```bash
dapr init -k
```

#### 1.3 Install Strimzi Kafka Operator
```bash
kubectl create -f https://strimzi.io/install/latest?namespace=kafka
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

#### 1.4 Deploy Kafka Cluster
```bash
kubectl apply -f infrastructure/kafka-config/strimzi-kafka-cluster.yaml
kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka --timeout=600s
```

#### 1.5 Build and Deploy Services
```bash
# Build service images
eval $(minikube docker-env)
docker build -t main-api:latest ./backend/main-api
docker build -t recurring-task-service:latest ./backend/recurring-task-service
docker build -t notification-service:latest ./backend/notification-service
docker build -t audit-service:latest ./backend/audit-service

# Deploy with Helm
helm upgrade --install todo-platform infrastructure/helm-charts/todo-platform/ --values infrastructure/helm-charts/todo-platform/values.yaml --create-namespace --namespace todo-app --wait
```

#### 1.6 Verify Deployment
```bash
kubectl get pods -n todo-app
kubectl get svc -n todo-app
kubectl get daprapps -n todo-app
```

### 2. Production Deployment

#### 2.1 Prerequisites Setup
```bash
# Authenticate with cloud provider
az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID  # For AKS
# OR
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS  # For GKE
# OR
aws eks update-kubeconfig --name $CLUSTER_NAME  # For EKS
```

#### 2.2 Install Dapr
```bash
helm repo add dapr https://dapr.github.io/helm-charts
helm repo update
helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait
```

#### 2.3 Install Kafka via Strimzi
```bash
kubectl create -f https://strimzi.io/install/latest?namespace=kafka
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
kubectl apply -f infrastructure/kafka-config/strimzi-kafka-cluster.yaml
kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka --timeout=600s
```

#### 2.4 Deploy Application
```bash
# Update image tags in values-prod.yaml with production images
helm upgrade --install todo-platform infrastructure/helm-charts/todo-platform/ \
  --values infrastructure/helm-charts/todo-platform/values-prod.yaml \
  --create-namespace --namespace todo-app --wait
```

## Configuration Management

### 1. Secret Management
- All secrets should be stored in Dapr secret stores
- Use Dapr's secret API for access
- Never commit secrets to version control

### 2. Environment-Specific Values
- `values-dev.yaml`: Development environment
- `values-staging.yaml`: Staging environment
- `values-prod.yaml`: Production environment

## Monitoring and Observability

### 1. Health Checks
Each service exposes a health endpoint at `/health`:
- Main API: `http://main-api:8000/health`
- Recurring Task Service: `http://recurring-task-service:8001/health`
- Notification Service: `http://notification-service:8002/health`
- Audit Service: `http://audit-service:8003/health`

### 2. Logging
- Centralized logging via ELK stack
- Structured JSON logs
- Access logs for all API endpoints

### 3. Metrics
- Prometheus metrics endpoint at `/metrics`
- Custom business metrics for task operations
- Service-level metrics (requests, errors, duration)

## Troubleshooting

### 1. Common Issues

#### Service Not Starting
Check pod status:
```bash
kubectl get pods -n todo-app
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app
```

#### Dapr Sidecar Issues
Check Dapr sidecar status:
```bash
kubectl get daprapps -n todo-app
kubectl logs <pod-name> -c daprd -n todo-app
```

#### Kafka Connectivity Issues
Check Kafka cluster status:
```bash
kubectl get kafka -n kafka
kubectl get pods -l strimzi.io/name=my-cluster-kafka -n kafka
```

#### Database Connection Issues
Verify database connectivity:
```bash
kubectl exec -it <pod-name> -n todo-app -- env | grep DB
kubectl logs <pod-name> -n todo-app | grep -i error
```

### 2. Performance Issues

#### High Memory Usage
```bash
kubectl top pods -n todo-app
kubectl describe pod <pod-name> -n todo-app  # Check resource limits
```

#### High CPU Usage
```bash
kubectl top pods -n todo-app
kubectl logs <pod-name> -n todo-app | grep -i "slow query\|timeout"
```

## Maintenance Procedures

### 1. Rolling Updates
```bash
# Update with zero downtime
helm upgrade --install todo-platform infrastructure/helm-charts/todo-platform/ \
  --set image.tag=new-tag --reuse-values
```

### 2. Backup and Restore
#### PostgreSQL Backup
```bash
kubectl exec -it postgres-pod -- pg_dump -U postgres todo_db > backup.sql
```

#### Kafka Topic Backup
```bash
# Kafka topics are replicated and durable by design
# Monitor replication status
kubectl exec -it my-cluster-kafka-0 -- bin/kafka-topics.sh --describe --bootstrap-server localhost:9092
```

### 3. Scaling
#### Vertical Scaling
Update resource requests/limits in Helm values:
```yaml
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi
```

#### Horizontal Scaling
```bash
kubectl scale deployment main-api -n todo-app --replicas=3
```

## Rollback Procedures

### 1. Helm Rollback
```bash
# Check revision history
helm history todo-platform -n todo-app

# Rollback to previous version
helm rollback todo-platform -n todo-app
```

### 2. Manual Rollback
```bash
# Scale down new deployment
kubectl scale deployment main-api -n todo-app --replicas=0

# Scale up previous version
kubectl scale deployment main-api-v1 -n todo-app --replicas=2
```

## Security Considerations

### 1. Network Policies
- Restrict traffic between namespaces
- Only allow necessary inter-service communication
- Use service accounts with minimal required permissions

### 2. Image Security
- Scan images for vulnerabilities before deployment
- Use minimal base images (e.g., alpine)
- Regularly update base images

### 3. Access Controls
- Use RBAC for Kubernetes access
- Implement least-privilege principle
- Rotate credentials regularly