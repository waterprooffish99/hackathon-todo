# Data Model for Kubernetes Deployment

## Kubernetes Entities

### Deployment
- **Name**: Unique identifier for the deployment
- **Replicas**: Number of desired pod instances
- **Image**: Container image reference
- **Ports**: Exposed ports for the container
- **Resources**: CPU and memory requests/limits
- **Environment**: Configuration variables
- **Labels**: Metadata for identification and selection

### Service
- **Name**: Unique identifier for the service
- **Type**: Service type (ClusterIP, NodePort, LoadBalancer)
- **Selector**: Labels to match pods
- **Ports**: Port mappings (targetPort, port, nodePort)
- **Annotations**: Additional metadata

### ConfigMap
- **Name**: Unique identifier for the config map
- **Data**: Key-value pairs of configuration data
- **Namespace**: Namespace for the config map

### Secret
- **Name**: Unique identifier for the secret
- **Data**: Base64 encoded sensitive data
- **Type**: Secret type (generic, TLS, etc.)

## Helm Chart Components

### Chart.yaml
- **Name**: Chart name
- **Version**: Chart version
- **Description**: Brief description of the chart
- **Dependencies**: List of dependent charts

### values.yaml
- **replicaCount**: Number of pod replicas
- **image.repository**: Container image repository
- **image.tag**: Container image tag
- **image.pullPolicy**: Image pull policy
- **service.type**: Kubernetes service type
- **service.port**: Service port
- **resources**: Resource requests and limits
- **nodeSelector**: Node selection constraints
- **tolerations**: Taint tolerations
- **affinity**: Pod affinity rules

## Deployment Configuration

### Frontend Service
- **Image**: todo-frontend
- **Port**: 3000 (typical for Next.js)
- **Environment Variables**:
  - BACKEND_URL: URL of the backend service
  - NEXT_PUBLIC_API_URL: Public API endpoint

### Backend Service
- **Image**: todo-backend
- **Port**: 8000 (typical for FastAPI)
- **Environment Variables**:
  - DATABASE_URL: PostgreSQL connection string
  - AUTH_SECRET: Authentication secret
  - REDIS_URL: Redis connection string (if used)

## Network Configuration

### Service Discovery
- **Backend Service**: backend-service.default.svc.cluster.local
- **Frontend Service**: frontend-service.default.svc.cluster.local

### External Access
- **NodePort Range**: 30000-32767
- **Frontend NodePort**: 30080 (mapped to port 3000)
- **Backend NodePort**: 30800 (mapped to port 8000)