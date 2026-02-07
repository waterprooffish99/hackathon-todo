#!/bin/bash

# Production Deployment Script for Cloud-Native AI Todo Platform
# This script deploys the platform to a production Kubernetes cluster

set -e  # Exit immediately if a command exits with a non-zero status

# Configuration variables
CLUSTER_NAME=${CLUSTER_NAME:-"todo-platform-prod"}
NAMESPACE=${NAMESPACE:-"todo-app"}
HELM_VALUES_FILE=${HELM_VALUES_FILE:-"infrastructure/helm-charts/todo-platform/values-prod.yaml"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
TIMEOUT=${TIMEOUT:-"10m"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}Cloud-Native AI Todo Platform${NC}"
    echo -e "${GREEN}Production Deployment${NC}"
    echo -e "${GREEN}================================${NC}"
    echo
}

print_step() {
    echo -e "${YELLOW}>>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        exit 1
    fi

    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        print_error "helm is not installed"
        exit 1
    fi

    # Check if dapr is installed
    if ! command -v dapr &> /dev/null; then
        print_error "dapr is not installed"
        exit 1
    fi

    # Check if we have kubectl access to the cluster
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Unable to connect to Kubernetes cluster"
        exit 1
    fi

    print_success "All prerequisites satisfied"
}

# Install Dapr
install_dapr() {
    print_step "Installing/Updating Dapr..."

    # Check if Dapr is already installed
    if kubectl get namespace dapr-system &> /dev/null; then
        print_step "Dapr already installed, checking version..."
        dapr status -k
    else
        print_step "Installing Dapr..."
        helm repo add dapr https://dapr.github.io/helm-charts
        helm repo update
        helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait
    fi

    print_success "Dapr is ready"
}

# Install Kafka via Strimzi
install_kafka() {
    print_step "Installing/Updating Kafka with Strimzi..."

    # Check if Kafka namespace exists
    if ! kubectl get namespace kafka &> /dev/null; then
        kubectl create namespace kafka
    fi

    # Install Strimzi
    kubectl create -f https://strimzi.io/install/latest?namespace=kafka
    kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

    # Deploy Kafka cluster
    if kubectl get kafka my-cluster &> /dev/null; then
        print_step "Kafka cluster already exists, updating..."
        kubectl apply -f infrastructure/kafka-config/strimzi-kafka-cluster.yaml
    else
        print_step "Creating Kafka cluster..."
        kubectl apply -f infrastructure/kafka-config/strimzi-kafka-cluster.yaml
    fi

    # Wait for Kafka to be ready
    kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka --timeout=600s

    print_success "Kafka is ready"
}

# Build and push Docker images
build_images() {
    print_step "Building Docker images..."

    # Build main API service
    docker build -t todo-main-api:${IMAGE_TAG} backend/main-api/ --platform linux/amd64

    # Build recurring task service
    docker build -t todo-recurring-task-service:${IMAGE_TAG} backend/recurring-task-service/ --platform linux/amd64

    # Build notification service
    docker build -t todo-notification-service:${IMAGE_TAG} backend/notification-service/ --platform linux/amd64

    # Build audit service
    docker build -t todo-audit-service:${IMAGE_TAG} backend/audit-service/ --platform linux/amd64

    print_success "Docker images built successfully"
}

# Push images to registry (this would be customized based on your registry)
push_images() {
    print_step "Pushing Docker images to registry..."

    # This is a placeholder - in a real environment you would:
    # 1. Tag images with registry URL
    # 2. Login to registry
    # 3. Push images

    # Example:
    # docker tag todo-main-api:${IMAGE_TAG} ${REGISTRY_URL}/todo-main-api:${IMAGE_TAG}
    # docker push ${REGISTRY_URL}/todo-main-api:${IMAGE_TAG}

    print_step "Images would be pushed to registry in real environment"
    print_success "Image pushing completed (simulated)"
}

# Deploy the application with Helm
deploy_application() {
    print_step "Deploying application with Helm..."

    # Create namespace if it doesn't exist
    if ! kubectl get namespace ${NAMESPACE} &> /dev/null; then
        kubectl create namespace ${NAMESPACE}
    fi

    # Add labels for monitoring
    kubectl label namespace ${NAMESPACE} name=${NAMESPACE} --overwrite

    # Install/upgrade the application
    if helm status todo-platform -n ${NAMESPACE} &> /dev/null; then
        print_step "Upgrading existing deployment..."
        helm upgrade todo-platform infrastructure/helm-charts/todo-platform/ \
            --namespace ${NAMESPACE} \
            --values ${HELM_VALUES_FILE} \
            --set image.tag=${IMAGE_TAG} \
            --timeout=${TIMEOUT} \
            --wait
    else
        print_step "Installing new deployment..."
        helm install todo-platform infrastructure/helm-charts/todo-platform/ \
            --namespace ${NAMESPACE} \
            --create-namespace \
            --values ${HELM_VALUES_FILE} \
            --set image.tag=${IMAGE_TAG} \
            --timeout=${TIMEOUT} \
            --wait
    fi

    print_success "Application deployed successfully"
}

# Verify deployment
verify_deployment() {
    print_step "Verifying deployment..."

    # Wait for all pods to be ready
    echo "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-platform -n ${NAMESPACE} --timeout=300s

    # Check pod statuses
    PODS_STATUS=$(kubectl get pods -n ${NAMESPACE} -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}')
    echo "Pod statuses:"
    echo -e "${PODS_STATUS}"

    # Check for any failed pods
    FAILED_PODS=$(echo "${PODS_STATUS}" | grep -c "Failed\|Error" || true)
    if [ "$FAILED_PODS" -gt 0 ]; then
        print_error "Some pods are in failed state"
        exit 1
    fi

    # Check Dapr sidecars
    DAPR_READY=$(kubectl get pods -n ${NAMESPACE} -o jsonpath='{range .items[*]}{range @.spec.containers}{@.name}{"\n"}{end}{end}' | grep daprd | wc -l)
    TOTAL_PODS=$(kubectl get pods -n ${NAMESPACE} --no-headers | wc -l)

    if [ "$DAPR_READY" -lt "$TOTAL_PODS" ]; then
        print_error "Not all pods have Dapr sidecars ready"
        exit 1
    fi

    print_success "Deployment verification passed"
}

# Run post-deployment tests
run_post_deployment_tests() {
    print_step "Running post-deployment tests..."

    # Run health checks on services
    MAIN_API_POD=$(kubectl get pods -n ${NAMESPACE} -l app=main-api -o jsonpath='{.items[0].metadata.name}')
    if [ -z "$MAIN_API_POD" ]; then
        print_error "Could not find main API pod"
        exit 1
    fi

    # Test health endpoint
    HEALTH_STATUS=$(kubectl exec -n ${NAMESPACE} $MAIN_API_POD -- curl -s http://localhost:8000/health | jq -r '.status')
    if [ "$HEALTH_STATUS" != "healthy" ]; then
        print_error "Main API health check failed"
        exit 1
    fi

    print_success "Post-deployment tests passed"
}

# Display deployment information
display_deployment_info() {
    print_step "Deployment Information:"

    echo "Namespace: ${NAMESPACE}"
    echo "Cluster: ${CLUSTER_NAME}"
    echo "Image Tag: ${IMAGE_TAG}"
    echo

    echo "Services:"
    kubectl get svc -n ${NAMESPACE}
    echo

    echo "Deployments:"
    kubectl get deployments -n ${NAMESPACE}
    echo

    echo "Dapr Applications:"
    kubectl get daprapps -n ${NAMESPACE}
    echo

    # Get external IP/URL if available
    EXTERNAL_IP=$(kubectl get svc -n ${NAMESPACE} main-api -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ ! -z "$EXTERNAL_IP" ]; then
        echo "External Access:"
        echo "  API: http://${EXTERNAL_IP}:80"
    fi
}

# Main execution
main() {
    print_header

    check_prerequisites
    install_dapr
    install_kafka
    build_images
    push_images
    deploy_application
    verify_deployment
    run_post_deployment_tests
    display_deployment_info

    print_success "Production deployment completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Monitor the application for any issues"
    echo "2. Run smoke tests to ensure all functionality works"
    echo "3. Update DNS records if needed"
    echo "4. Notify stakeholders of the deployment"
}

# Run main function
main "$@"