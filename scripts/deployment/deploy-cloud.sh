#!/bin/bash

# Deployment script for cloud providers (AKS, GKE, EKS)

set -e  # Exit immediately if a command exits with a non-zero status

usage() {
    echo "Usage: $0 -c <cloud-provider> -n <cluster-name> -r <region>"
    echo "  -c: Cloud provider (aks, gke, eks)"
    echo "  -n: Cluster name"
    echo "  -r: Region"
    exit 1
}

while getopts "c:n:r:h" opt; do
    case $opt in
        c) CLOUD_PROVIDER="$OPTARG" ;;
        n) CLUSTER_NAME="$OPTARG" ;;
        r) REGION="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

if [[ -z "$CLOUD_PROVIDER" || -z "$CLUSTER_NAME" || -z "$REGION" ]]; then
    usage
fi

echo "Starting deployment to $CLOUD_PROVIDER..."

case $CLOUD_PROVIDER in
    "aks")
        echo "Setting up Azure AKS..."
        # Login to Azure (assumes az CLI is installed and configured)
        az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID

        # Get AKS credentials
        az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME

        # Install Dapr
        helm repo add dapr https://dapr.github.io/helm-charts
        helm repo update
        helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait

        # Install Strimzi Kafka Operator
        kubectl create -f https://strimzi.io/install/latest?namespace=kafka
        kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

        # Deploy Kafka cluster
        kubectl apply -f ../kafka-config/strimzi-kafka-cluster.yaml
        kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka --timeout=600s
        ;;

    "gke")
        echo "Setting up Google GKE..."
        # Login to Google Cloud (assumes gcloud CLI is installed and configured)
        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
        gcloud config set project $GCP_PROJECT_ID

        # Get GKE credentials
        gcloud container clusters get-credentials $CLUSTER_NAME --zone $REGION --project $GCP_PROJECT_ID

        # Install Dapr
        helm repo add dapr https://dapr.github.io/helm-charts
        helm repo update
        helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait

        # Install Strimzi Kafka Operator
        kubectl create -f https://strimzi.io/install/latest?namespace=kafka
        kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

        # Deploy Kafka cluster
        kubectl apply -f ../kafka-config/strimzi-kafka-cluster.yaml
        kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka --timeout=600s
        ;;

    "eks")
        echo "Setting up Amazon EKS..."
        # Configure AWS credentials (assumes aws CLI is installed and configured)
        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
        export AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION

        # Update kubeconfig for EKS cluster
        aws eks update-kubeconfig --name $CLUSTER_NAME --region $REGION

        # Install Dapr
        helm repo add dapr https://dapr.github.io/helm-charts
        helm repo update
        helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait

        # Install Strimzi Kafka Operator
        kubectl create -f https://strimzi.io/install/latest?namespace=kafka
        kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

        # Deploy Kafka cluster
        kubectl apply -f ../kafka-config/strimzi-kafka-cluster.yaml
        kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka --timeout=600s
        ;;

    *)
        echo "Unsupported cloud provider: $CLOUD_PROVIDER"
        echo "Supported providers: aks, gke, eks"
        exit 1
        ;;
esac

echo "Deploying the application..."
# Install the main application
helm upgrade --install todo-platform ../helm-charts/todo-platform/ --values ../helm-charts/todo-platform/values.yaml --create-namespace --namespace todo-app --wait

echo "Deployment to $CLOUD_PROVIDER completed!"
kubectl get pods -n todo-app
echo "Application deployed to cluster: $CLUSTER_NAME"