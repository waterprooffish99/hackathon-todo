#!/bin/bash

# Deployment script for Minikube environment

set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting deployment to Minikube..."

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --disk-size=20g
fi

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Set docker environment to minikube
eval $(minikube docker-env)

echo "Building service images..."
# Build the service images
docker build -t main-api:latest ./backend/main-api
docker build -t recurring-task-service:latest ./backend/recurring-task-service
docker build -t notification-service:latest ./backend/notification-service
docker build -t audit-service:latest ./backend/audit-service

echo "Installing Dapr..."
# Install Dapr in Minikube
helm repo add dapr https://dapr.github.io/helm-charts
helm repo update
helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait

echo "Installing Strimzi Kafka Operator..."
# Install Strimzi Kafka Operator
kubectl create -f https://strimzi.io/install/latest?namespace=kafka
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

echo "Deploying Kafka cluster..."
# Deploy Kafka cluster
kubectl apply -f ../kafka-config/strimzi-kafka-cluster.yaml
kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka --timeout=600s

echo "Deploying the application..."
# Install the main application
helm upgrade --install todo-platform ../helm-charts/todo-platform/ --values ../helm-charts/todo-platform/values.yaml --create-namespace --namespace todo-app --wait

echo "Deployment to Minikube completed!"
echo "Application is available at: $(minikube ip)"
echo "Dapr dashboard: dapr dashboard"
echo "To access the application: minikube service -n todo-app main-api --url"